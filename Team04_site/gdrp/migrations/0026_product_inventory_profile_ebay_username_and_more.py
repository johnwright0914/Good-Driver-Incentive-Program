# Generated by Django 4.1.6 on 2023-04-11 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('gdrp', '0025_product_inventory_alter_product_catalog_productids'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('approved', models.BooleanField(default=False)),
                ('sponsor', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='gdrp.sponsor')),
            ],
        ),
    ]