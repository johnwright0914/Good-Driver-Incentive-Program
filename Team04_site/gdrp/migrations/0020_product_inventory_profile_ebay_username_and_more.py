# Generated by Django 4.1.6 on 2023-04-06 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0019_product_inventory_profile_ebay_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(default='[Product Description]', max_length=5500),
        ),
    ]
