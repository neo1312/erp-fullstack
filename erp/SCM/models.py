from django.db import models
from django.apps import apps

class Provedor(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    fiability_score = models.FloatField(default=0.0)  # Reliability score (1-5)
    credit_score = models.FloatField(default=0.0)  # Payment terms score (1-5)
    cost_dropping_score = models.FloatField(default=0.0)  # Price dropping score (1-5)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Provedor, on_delete=models.CASCADE)  # Supplier
    created_at = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total cost
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
    )

    def calculate_total_cost(self):
        """ Calculate the total cost based on related items. """
        self.total_cost = sum(item.total_price() for item in self.items.all())
        self.save()

    def complete_purchase(self):
        """ Finalize purchase and add items to inventory. """
        for item in self.items.all():
            item.add_to_inventory()
        self.status = "completed"
        self.save()

    def __str__(self):
        return f"Purchase Order {self.id} - {self.supplier.nombre} - {self.status}"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey("SCM.PurchaseOrder", on_delete=models.CASCADE, related_name="items")
    producto_hijo = models.ForeignKey("IM.Producto_hijo", on_delete=models.CASCADE)
    supplier = models.ForeignKey("SCM.Provedor", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Auto-filled
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        Provedor_Producto = apps.get_model('IM', 'Provedor_Producto')
        # Fetch the cost from the Provedor_Producto relationship
        proveedor_producto = Provedor_Producto.objects.filter(
            producto=self.producto_hijo,
            provedor=self.supplier
        ).first()
        
        if proveedor_producto:
            self.unit_cost = proveedor_producto.costo  # Auto-fill unit cost
        
        self.total_cost = self.unit_cost * self.quantity if self.unit_cost else 0  # Calculate total cost
        
        super().save(*args, **kwargs)  # Call parent save method

    def __str__(self):
        return f"{self.producto_hijo} - {self.supplier} - {self.quantity} x ${self.unit_cost}"

