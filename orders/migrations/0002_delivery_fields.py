# Generated manually for delivery fields update

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='city',
        ),
        migrations.RemoveField(
            model_name='order',
            name='postal_code',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(choices=[('delivery', 'Delivery'), ('collection', 'Collection at Star Mall CBD')], default='delivery', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='distance_km',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='order',
            name='exact_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='house_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]