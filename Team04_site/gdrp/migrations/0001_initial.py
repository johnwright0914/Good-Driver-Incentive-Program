# Generated by Django 4.1.6 on 2023-02-15 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Product', max_length=255)),
                ('description', models.CharField(default='[Product Description]', max_length=255)),
                ('price_dollars', models.FloatField(default=0.0)),
                ('image', models.CharField(default='no image', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Sponsor', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(default='a@b.c', max_length=254)),
                ('user_type', models.CharField(default='Driver', max_length=50)),
                ('name', models.CharField(default='first last', max_length=255)),
                ('points', models.IntegerField(default=0)),
                ('SponsorID', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='gdrp.sponsor')),
            ],
        ),
        migrations.CreateModel(
            name='Product_catalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ProductIDs', models.ManyToManyField(to='gdrp.product')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_time', models.DateTimeField()),
                ('point_total', models.IntegerField(default=0)),
                ('UserID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gdrp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversion_rate', models.FloatField(default=0.01)),
                ('product_catalog', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='gdrp.product_catalog')),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gdrp.sponsor')),
            ],
        ),
        migrations.CreateModel(
            name='Order_Details',
            fields=[
                ('OderID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='gdrp.order')),
                ('quantity', models.IntegerField(default=0)),
                ('products', models.ManyToManyField(to='gdrp.product')),
            ],
        ),
    ]
