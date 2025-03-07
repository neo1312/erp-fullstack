from django.db import models
from django.utils import timezone
from SCM.models import Provedor
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

class Marca(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


class Producto_padre(models.Model):
    UNIT_CHOICES = [
        ('gramos', 'Gramos'),
        ('kilos', 'Kilos'),
        ('piezas', 'Piezas'),
        ('metros', 'Metros')
    ]

    name = models.CharField(max_length=255, unique=True)
    stock_min = models.IntegerField(default=0)
    stock_max = models.IntegerField(default=0)
    unidad_granel = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piezas')
    granel = models.BooleanField(default=False)  # If product is sold in bulk
    active = models.BooleanField(default=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)  # Unified selling price

    @property
    def total_stock(self):
        """ Calculate total stock by summing all child products' stock. """
        return sum(variant.stock for variant in self.variants.all())

    def update_selling_price(self, new_price):
        """ Update selling price for all child products and inventory items. """
        self.precio_venta = new_price
        self.save()

        # Update all variants under this parent
        for variant in self.variants.all():
            variant.update_inventory_prices(new_price)

    def __str__(self):
        return f"{self.name} (Total Stock: {self.total_stock})"


class Producto_hijo(models.Model):
    producto_padre = models.ForeignKey(Producto_padre, related_name="variants", on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True)
    codigo_barras = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def update_inventory_prices(self, new_price):
        """ Update selling price of all inventory items under this variant. """
        InventoryItem.objects.filter(product=self).update(selling_price=new_price)

    def __str__(self):
        return f"{self.producto_padre.name} - {self.marca.nombre if self.marca else 'No Brand'}"


class Provedor_Producto(models.Model):
    producto = models.ForeignKey(Producto_hijo, on_delete=models.CASCADE, related_name="provider")
    provedor = models.ForeignKey(Provedor, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_compra = models.CharField(max_length=50)  # Purchase unit
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['producto', 'provedor'], name='unique_proveedor_producto')
        ]

    def __str__(self):
        return f"{self.producto.producto_padre.name} - {self.producto.marca} - {self.provedor.nombre} (${self.costo})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        ProveedorProductoScore.calculate_scores_for_father_product(self.producto.producto_padre)


class ProveedorProductoScore(models.Model):
    provedor_producto = models.OneToOneField(Provedor_Producto, on_delete=models.CASCADE, related_name="score")
    cost_score = models.FloatField(default=0.0)  # 1-5 
    unidad_compra_score = models.FloatField(default=0.0)  # 1-5 

    @staticmethod
    def calculate_scores_for_father_product(producto_padre):
        """
        Recalculate and update scores for all Proveedor_Producto items under the same Producto_padre
        """
        #Get all proveedor_producto items linked to the given Producto_padre
        all_proveedores = Provedor_Producto.objects.filter(producto__producto_padre=producto_padre)
        if not all_proveedores.exists():
            return #No porducts to update

        #Extract cost and uniddad_ compra values
        costs = [p.costo for p in all_proveedores]
        unidades = [float(p.unidad_compra) for p in all_proveedores]

        #calculate min/max values
        min_cost, max_cost = min(costs), max(costs)
        min_unidad, max_unidad = min(unidades), max(unidades)

        # Update each Proveedor_Producto's score
        for proveedor in all_proveedores:
            score_instance, created = ProveedorProductoScore.objects.get_or_create(provedor_producto=proveedor)

            # Assign cost_score (min cost = 5, max cost = 1)
            if max_cost == min_cost:
                score_instance.cost_score = 5  # If only one value, give it max score
            else:
                score_instance.cost_score = round(5 - ((proveedor.costo - min_cost) / (max_cost - min_cost)) * 4, 2)

            # Assign unidad_compra_score (min unidad = 5, max unidad = 1)
            if max_unidad == min_unidad:
                score_instance.unidad_compra_score = 5
            else:
                score_instance.unidad_compra_score = round(
                    5 - ((float(proveedor.unidad_compra) - min_unidad) / (max_unidad - min_unidad)) * 4, 2
                )

            # Save the updated score
            score_instance.save()




def calculate_overall_score(self):
    weights = {
        'cost_score': 0.4,  # Example weight for cost score
        'unidad_compra_score': 0.3,  # Example weight for minimum purchase score
        'fiability': 0.2,  # Example weight for fiability score
        'credit': 0.1,  # Example weight for credit score
        'cost_dropping': 0.1  # Example weight for cost dropping score
    }

    overall_score = (
        self.cost_score * weights['cost_score'] +
        self.unidad_compra_score * weights['unidad_compra_score'] +
        self.provedor.fiability_score * weights['fiability'] +
        self.provedor.credit_score * weights['credit'] +
        self.provedor.cost_dropping_score * weights['cost_dropping']
    )
    return overall_score



class InventoryItem(models.Model):
    producto_hijo = models.ForeignKey("Producto_hijo", on_delete=models.CASCADE, related_name="inventory_items")
    sequential_id = models.PositiveIntegerField()  # Unique per product
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # Purchase price
    supplier = models.ForeignKey(Provedor, on_delete=models.SET_NULL, null=True, blank=True)  # Supplier
    date_added = models.DateTimeField(default=now)
    sold = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Sale price when sold
    date_sold = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('producto_hijo', 'sequential_id')  # Ensures sequential_id is unique per product

    def set_selling_price(self):
        """ Set selling price based on the parent product's price. """
        self.selling_price = self.product.producto_padre.precio_venta
        self.save()

    def calculate_profit(self):
        """ Calculate profit when the item is sold. """
        if self.selling_price and self.purchase_price:
            return self.selling_price - self.purchase_price
        return 0

    def __str__(self):
        return f"{self.product.producto_padre.name} - {self.product.marca} - ID: {self.internal_id}"



