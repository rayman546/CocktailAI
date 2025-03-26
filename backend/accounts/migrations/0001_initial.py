"""
Initial migration for the accounts app.
"""

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(blank=True, max_length=20, verbose_name='Phone Number')),
                ('position', models.CharField(blank=True, max_length=100, verbose_name='Position/Role')),
                ('bio', models.TextField(blank=True, verbose_name='Biography')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/', verbose_name='Profile Image')),
                ('notification_email', models.BooleanField(default=True, verbose_name='Email Notifications')),
                ('notification_sms', models.BooleanField(default=False, verbose_name='SMS Notifications')),
                ('dark_mode', models.BooleanField(default=False, verbose_name='Dark Mode')),
                ('company_name', models.CharField(blank=True, max_length=255, verbose_name='Company Name')),
                ('location', models.CharField(blank=True, max_length=255, verbose_name='Location')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date Updated')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items_per_page', models.PositiveIntegerField(default=20, verbose_name='Items Per Page')),
                ('default_view', models.CharField(choices=[('list', 'List'), ('grid', 'Grid'), ('calendar', 'Calendar')], default='list', max_length=50, verbose_name='Default View')),
                ('low_stock_alerts', models.BooleanField(default=True, verbose_name='Low Stock Alerts')),
                ('order_status_notifications', models.BooleanField(default=True, verbose_name='Order Status Notifications')),
                ('inventory_count_reminders', models.BooleanField(default=True, verbose_name='Inventory Count Reminders')),
                ('date_format', models.CharField(default='MM/DD/YYYY', max_length=20, verbose_name='Date Format')),
                ('time_format', models.CharField(default='12-hour', max_length=20, verbose_name='Time Format')),
                ('timezone', models.CharField(default='UTC', max_length=50, verbose_name='Timezone')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='accounts.user')),
            ],
            options={
                'verbose_name': 'User Preferences',
                'verbose_name_plural': 'User Preferences',
            },
        ),
    ] 