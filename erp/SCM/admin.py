from django.contrib import admin
from .models import Provedor,PurchaseOrder,PurchaseOrderItem

admin.site.register(Provedor)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
# Register your models here.
