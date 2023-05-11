# Generated by Django 4.1.6 on 2023-04-19 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0001_squashed_0026_product_inventory_profile_ebay_username_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='[Product Description]', null=True),
        ),
    ]
