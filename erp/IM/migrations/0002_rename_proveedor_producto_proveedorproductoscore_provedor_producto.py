# Generated by Django 5.1.6 on 2025-02-08 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('IM', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proveedorproductoscore',
            old_name='proveedor_producto',
            new_name='provedor_producto',
        ),
    ]
