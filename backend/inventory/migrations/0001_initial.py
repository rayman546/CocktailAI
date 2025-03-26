"""
Initial migration for the inventory app.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('is_storage', models.BooleanField(default=False, verbose_name='Is Storage Location')),
                ('is_service', models.BooleanField(default=False, verbose_name='Is Service Location')),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('contact_name', models.CharField(blank=True, max_length=255, verbose_name='Contact Name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Phone')),
                ('address', models.TextField(blank=True, verbose_name='Address')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Supplier',
                'verbose_name_plural': 'Suppliers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('sku', models.CharField(blank=True, max_length=50, verbose_name='SKU')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Image')),
                ('barcode', models.CharField(blank=True, max_length=100, verbose_name='Barcode')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)], verbose_name='Unit Price')),
                ('unit_size', models.DecimalField(decimal_places=2, help_text='Size of the unit (e.g., 750ml for a standard wine bottle)', max_digits=10, validators=[MinValueValidator(0)], verbose_name='Unit Size')),
                ('unit_type', models.CharField(choices=[('bottle', 'Bottle'), ('can', 'Can'), ('keg', 'Keg'), ('case', 'Case'), ('box', 'Box'), ('each', 'Each'), ('weight', 'Weight'), ('volume', 'Volume')], default='bottle', max_length=20, verbose_name='Unit Type')),
                ('par_level', models.DecimalField(decimal_places=2, default=0, help_text='Target inventory level to maintain', max_digits=10, validators=[MinValueValidator(0)], verbose_name='Par Level')),
                ('reorder_point', models.DecimalField(decimal_places=2, default=0, help_text='Inventory level at which to reorder', max_digits=10, validators=[MinValueValidator(0)], verbose_name='Reorder Point')),
                ('reorder_quantity', models.DecimalField(decimal_places=2, default=1, help_text='Quantity to reorder when reorder point is reached', max_digits=10, validators=[MinValueValidator(0)], verbose_name='Reorder Quantity')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='inventory.category', verbose_name='Category')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='inventory.supplier', verbose_name='Supplier')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['name'],
                'unique_together': {('supplier', 'sku')},
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[MinValueValidator(0)], verbose_name='Quantity')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='inventory.location', verbose_name='Location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='inventory.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Inventory Item',
                'verbose_name_plural': 'Inventory Items',
                'unique_together': {('product', 'location')},
            },
        ),
    ] 