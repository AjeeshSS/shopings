# Generated by Django 4.1.4 on 2023-03-13 05:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_orderplaced_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='brand_image',
            field=models.ImageField(upload_to='productimg', validators=[django.core.validators.FileExtensionValidator(['jpeg', 'png', 'jpg'])]),
        ),
    ]
