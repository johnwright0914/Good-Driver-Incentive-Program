# Generated by Django 4.1.6 on 2023-04-05 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0013_product_inventory_alter_product_categories_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='no image', max_length=255, upload_to=''),
        ),
    ]
