# Generated by Django 4.1.6 on 2023-03-13 13:16

from django.db import migrations, models
import gdrp.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0007_alter_product_catalog_productids'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Promotion', max_length=255)),
                ('description', models.CharField(default='#PROMO_DESCRIPTION', max_length=255)),
                ('multiplier', models.FloatField(default=1.0)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=gdrp.fields.SeparatedTextField(blank=True),
        ),
    ]
