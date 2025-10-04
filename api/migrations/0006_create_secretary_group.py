# api/migrations/0006_create_secretary_group.py

from django.db import migrations

def create_secretary_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Secretary')

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_auditlog_client'),
    ]

    operations = [
        migrations.RunPython(create_secretary_group),
    ]