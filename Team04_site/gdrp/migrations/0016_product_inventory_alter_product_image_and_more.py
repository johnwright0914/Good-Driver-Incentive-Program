# Generated by Django 4.1.6 on 2023-04-05 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0015_product_inventory_alter_product_catalog_productids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='', max_length=255, null=True, upload_to=''),
        ),
    ]
