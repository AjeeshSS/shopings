# Generated by Django 4.1.4 on 2023-03-12 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_orderplaced_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderplaced',
            name='discount',
        ),
    ]
