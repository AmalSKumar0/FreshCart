# Generated by Django 5.1.5 on 2025-02-16 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0003_alter_price_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_veg',
            field=models.BooleanField(default=True),
        ),
    ]
