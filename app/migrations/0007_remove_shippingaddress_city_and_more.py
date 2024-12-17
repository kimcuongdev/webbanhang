# Generated by Django 5.1.2 on 2024-11-30 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_order_complete_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='city',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='state',
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]