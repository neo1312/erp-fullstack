from django.contrib import admin
from .models import Producto_padre, Producto_hijo,Provedor_Producto,Marca,ProveedorProductoScore, InventoryItem

admin.site.register(Marca)
admin.site.register(ProveedorProductoScore)
admin.site.register(Provedor_Producto)
admin.site.register(Producto_padre)
admin.site.register(Producto_hijo)
admin.site.register(InventoryItem)

