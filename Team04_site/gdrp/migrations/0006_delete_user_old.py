# Generated by Django 4.1.6 on 2023-02-21 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gdrp', '0005_remove_profile_id_profile_phone_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User_old',
        ),
    ]
