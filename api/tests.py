# api/tests.py

from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.utils import timezone
from .models import Client, Equipment, ServiceHistory, Note, Invoice, MaintenanceReminder, AuditLog, UserProfile, Appointment
from datetime import timedelta

class PermissionTests(APITestCase):

    def setUp(self):
        # Create user groups
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.technician_group, _ = Group.objects.get_or_create(name='Technician')

        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='password123')
        self.technician_user = User.objects.create_user(username='technician', password='password123')
        self.normal_user = User.objects.create_user(username='normaluser', password='password123')

        # Assign users to groups
        self.admin_user.groups.add(self.admin_group)
        self.technician_user.groups.add(self.technician_group)

        # Create tokens for authentication
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.technician_token, _ = Token.objects.get_or_create(user=self.technician_user)
        self.normal_user_token, _ = Token.objects.get_or_create(user=self.normal_user)

        # Authenticate clients
        self.admin_client = self.client
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        # Create a separate client for the technician
        self.technician_client = self.client_class()
        self.technician_client.credentials(HTTP_AUTHORIZATION='Token ' + self.technician_token.key)

        # Create a separate client for the normal user
        self.normal_user_client = self.client_class()
        self.normal_user_client.credentials(HTTP_AUTHORIZATION='Token ' + self.normal_user_token.key)

        # Create sample data
        self.client_obj = Client.objects.create(first_name='Test', last_name='Client', email='test@example.com')

    def test_client_permissions(self):
        # Admin should have full access
        response = self.admin_client.get('/api/clients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Technician should have read-only access
        response = self.technician_client.get('/api/clients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.technician_client.post('/api/clients/', {'first_name': 'New', 'last_name': 'Client', 'email': 'new@example.com'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user should have no access
        response = self.normal_user_client.get('/api/clients/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invoice_permissions(self):
        # Admin should have full access
        response = self.admin_client.get('/api/invoices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Technician should have no access
        response = self.technician_client.get('/api/invoices/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_service_history_permissions(self):
        # Admin can create and read
        response = self.admin_client.get('/api/service-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Technician can create and read
        response = self.technician_client.get('/api/service-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        equipment = Equipment.objects.create(client=self.client_obj, equipment_type='Furnace')
        service_data = {'equipment': equipment.id, 'service_date': '2023-01-01', 'description': 'test', 'cost': 100}
        response = self.technician_client.post('/api/service-history/', service_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Technician cannot update
        service_history = ServiceHistory.objects.first()
        response = self.technician_client.put(f'/api/service-history/{service_history.id}/', {'description': 'updated'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class FeatureTests(APITestCase):
    def setUp(self):
        # Create user groups
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.technician_group, _ = Group.objects.get_or_create(name='Technician')

        # Create users
        self.admin_user = User.objects.create_user(username='admin_features', password='password123')
        self.technician_user = User.objects.create_user(username='technician_features', password='password123')

        # Assign users to groups
        self.admin_user.groups.add(self.admin_group)
        self.technician_user.groups.add(self.technician_group)

        # Create tokens for authentication
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.technician_token, _ = Token.objects.get_or_create(user=self.technician_user)

        # Authenticate clients
        self.admin_client = self.client_class()
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        self.technician_client = self.client_class()
        self.technician_client.credentials(HTTP_AUTHORIZATION='Token ' + self.technician_token.key)

        # Create sample data
        self.client_obj = Client.objects.create(first_name='Audit', last_name='Client', email='audit@example.com')
        self.equipment = Equipment.objects.create(client=self.client_obj, equipment_type='Coil')
        self.service_history = ServiceHistory.objects.create(equipment=self.equipment, service_date='2023-01-01', description='test', cost=100)

    def test_invoice_payment_fields(self):
        invoice = Invoice.objects.create(client=self.client_obj, service_history=self.service_history, invoice_date='2023-01-01', amount_due=100)

        # Update the invoice with payment details
        update_data = {'payment_method': 'Check', 'check_number': '12345', 'status': 'Paid'}
        response = self.admin_client.patch(f'/api/invoices/{invoice.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the fields were updated
        invoice.refresh_from_db()
        self.assertEqual(invoice.payment_method, 'Check')
        self.assertEqual(invoice.check_number, '12345')

    def test_audit_log_creation_and_user_tracking(self):
        # Test CREATE
        initial_log_count = AuditLog.objects.count()
        new_client_data = {'first_name': 'Log', 'last_name': 'Me', 'email': 'logme@example.com'}
        response = self.admin_client.post('/api/clients/', new_client_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_client_id = response.data['id']

        # Verify log entry for creation
        self.assertEqual(AuditLog.objects.count(), initial_log_count + 1)
        last_log = AuditLog.objects.latest('timestamp')
        self.assertEqual(last_log.action, 'CREATED Client')
        self.assertEqual(last_log.user, self.admin_user)

        # Test UPDATE
        update_data = {'first_name': 'Log', 'last_name': 'Me-Updated', 'email': 'logme@example.com'}
        response = self.admin_client.put(f'/api/clients/{new_client_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify log entry for update
        self.assertEqual(AuditLog.objects.count(), initial_log_count + 2)
        last_log = AuditLog.objects.latest('timestamp')
        self.assertEqual(last_log.action, 'UPDATED Client')
        self.assertEqual(last_log.user, self.admin_user)

        # Test DELETE
        response = self.admin_client.delete(f'/api/clients/{new_client_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify log entry for deletion
        self.assertEqual(AuditLog.objects.count(), initial_log_count + 3)
        last_log = AuditLog.objects.latest('timestamp')
        self.assertEqual(last_log.action, 'DELETED Client')
        self.assertEqual(last_log.user, self.admin_user)
        self.assertIsNone(last_log.client)

    def test_audit_log_endpoint_permissions(self):
        # Admin should have read access
        response = self.admin_client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Technician should be forbidden
        response = self.technician_client.get('/api/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CalendarFeatureTests(APITestCase):
    def setUp(self):
        # Create user groups
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.secretary_group, _ = Group.objects.get_or_create(name='Secretary')
        self.technician_group, _ = Group.objects.get_or_create(name='Technician')

        # Create users
        self.admin_user = User.objects.create_user(username='calendar_admin', password='password123')
        self.secretary_user = User.objects.create_user(username='secretary', password='password123')
        self.tech1 = User.objects.create_user(username='tech1', password='password123')
        self.tech2 = User.objects.create_user(username='tech2', password='password123')

        # Create profiles
        UserProfile.objects.create(user=self.admin_user, color='#FF0000')
        UserProfile.objects.create(user=self.secretary_user, color='#00FF00')
        UserProfile.objects.create(user=self.tech1, color='#0000FF')
        UserProfile.objects.create(user=self.tech2, color='#FFFF00')

        # Assign users to groups
        self.admin_user.groups.add(self.admin_group)
        self.secretary_user.groups.add(self.secretary_group)
        self.tech1.groups.add(self.technician_group)
        self.tech2.groups.add(self.technician_group)

        # Create tokens for authentication
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.secretary_token, _ = Token.objects.get_or_create(user=self.secretary_user)
        self.tech1_token, _ = Token.objects.get_or_create(user=self.tech1)

        # Authenticate clients
        self.admin_client = self.client_class()
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        self.secretary_client = self.client_class()
        self.secretary_client.credentials(HTTP_AUTHORIZATION='Token ' + self.secretary_token.key)
        self.tech1_client = self.client_class()
        self.tech1_client.credentials(HTTP_AUTHORIZATION='Token ' + self.tech1_token.key)

        # Create sample data
        self.client_obj = Client.objects.create(first_name='Calendar', last_name='Client', email='calendar@example.com')
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=2)

    def test_equipment_types(self):
        equipment_types = [choice[0] for choice in Equipment.EQUIPMENT_TYPE_CHOICES]
        self.assertIn('Tank Water Heater', equipment_types)
        self.assertIn('Tankless Water Heater', equipment_types)
        self.assertIn('Water Softener', equipment_types)
        self.assertIn('Mini Split', equipment_types)
        self.assertNotIn('Filter System', equipment_types)
        self.assertNotIn('Water Heater', equipment_types)

    def test_user_profile_color(self):
        response = self.tech1_client.get('/api/user-profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['color'], '#0000FF')

        profile_id = UserProfile.objects.get(user=self.tech1).id
        response = self.tech1_client.patch(f'/api/user-profiles/{profile_id}/', {'color': '#AAAAAA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = UserProfile.objects.get(user=self.tech1)
        self.assertEqual(profile.color, '#AAAAAA')

    def test_appointment_permissions(self):
        response = self.admin_client.post('/api/appointments/', {
            'title': 'Admin Test', 'client': self.client_obj.id, 'start_time': self.start_time,
            'end_time': self.end_time, 'technicians': [self.tech1.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment_id = response.data['id']

        response = self.secretary_client.patch(f'/api/appointments/{appointment_id}/', {'title': 'Secretary Update'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.tech1_client.get(f'/api/appointments/{appointment_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.tech1_client.patch(f'/api/appointments/{appointment_id}/', {'title': 'Tech Update Fail'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.secretary_client.delete(f'/api/appointments/{appointment_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_appointment_creation_and_conflict(self):
        response = self.admin_client.post('/api/appointments/', {
            'title': 'First Job', 'client': self.client_obj.id, 'start_time': self.start_time,
            'end_time': self.end_time, 'technicians': [self.tech1.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        conflicting_start_time = self.start_time + timedelta(hours=1)
        conflicting_end_time = conflicting_start_time + timedelta(hours=1)
        response = self.admin_client.post('/api/appointments/', {
            'title': 'Conflict Job', 'client': self.client_obj.id, 'start_time': conflicting_start_time,
            'end_time': conflicting_end_time, 'technicians': [self.tech1.id]
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already booked', str(response.data))

        response = self.admin_client.post('/api/appointments/', {
            'title': 'Concurrent Job', 'client': self.client_obj.id, 'start_time': self.start_time,
            'end_time': self.end_time, 'technicians': [self.tech2.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_appointment_filtering(self):
        Appointment.objects.create(
            title='Job A', client=self.client_obj, start_time=self.start_time,
            end_time=self.end_time
        ).technicians.add(self.tech1)

        next_day_start = self.start_time + timedelta(days=1)
        next_day_end = self.end_time + timedelta(days=1)
        Appointment.objects.create(
            title='Job B', client=self.client_obj, start_time=next_day_start,
            end_time=next_day_end
        ).technicians.add(self.tech2)

        start_date_str = self.start_time.strftime('%Y-%m-%d')
        response = self.admin_client.get(f'/api/appointments/?start_date={start_date_str}&end_date={start_date_str}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Job A')

        response = self.admin_client.get(f'/api/appointments/?technician_ids={self.tech2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Job B')