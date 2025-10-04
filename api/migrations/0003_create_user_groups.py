# api/migrations/0003_create_user_groups.py

from django.db import migrations

def create_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Technician')

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_invoice_maintenancereminder_note'),
    ]

    operations = [
        migrations.RunPython(create_user_groups),
    ]