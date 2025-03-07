from django.db import models
from datetime import timedelta, date
from django.utils import timezone
import math
from SCM.models import Provedor

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

    @property
    def total_stock(self):
        """Calculate total stock by summing all brand variants' stock."""
        return sum(variant.stock for variant in self.variants.all())

    def __str__(self):
        return f"{self.name} (Total Stock: {self.total_stock})"

class Producto_hijo(models.Model):
    producto_padre = models.ForeignKey(Producto_padre, related_name="variants", on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True)
    codigo_barras = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    precio1 = models.DecimalField(max_digits=10, decimal_places=2)
    precio2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio4 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.producto_padre.name} - {self.marca.nombre if self.marca else 'No Brand'}"

class Provedor_Producto(models.Model):
    producto = models.ForeignKey(Producto_hijo, on_delete=models.CASCADE, related_name="providers")
    provedor = models.ForeignKey(Provedor, on_delete=models.CASCADE)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_compra = models.CharField(max_length=50)  # Purchase unit
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('producto', 'provedor')  # Avoid duplicate provider-product entries

    def __str__(self):
        return f"{self.producto.producto_padre.name} - {self.producto.marca} - {self.provedor.nombre} (${self.costo})"

class ProveedorProductoScore(models.Model):
    proveedor_producto = models.OneToOneField(Provedor_Producto, on_delete=models.CASCADE, related_name="score")
    cost_score = models.FloatField(default=0.0)  # Score based on cost
    unidad_compra_score = models.FloatField(default=0.0)  # Score based on min amount

    def __str__(self):
        return f"Score for {self.proveedor_producto}"

