# api/models.py

from django.db import models
from django.contrib.auth.models import User

# =================================================================
# Core Models
# =================================================================

class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address_street = models.CharField(max_length=255, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=50, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=25, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, help_text="e.g., {'reminders': 'email'}")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    color = models.CharField(max_length=7, default='#FFFFFF', help_text="Hex color code for the user's calendar events")
    phone = models.CharField(max_length=25, blank=True)
    address = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# =================================================================
# Job & Scheduling Models
# =================================================================

class JobType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('partially_completed', 'Partially Completed'), ('pending', 'Pending')]
    title = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    technicians = models.ManyToManyField(User, related_name='appointments')
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    travel_time = models.PositiveIntegerField(default=0, help_text="Travel time in minutes")
    is_priority = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled')
    recurrence_rule = models.TextField(blank=True, help_text="iCal RRULE string")

    def __str__(self):
        return f"Appointment for {self.client} at {self.start_time}"

# =================================================================
# Equipment & Parts Models
# =================================================================

class Equipment(models.Model):
    EQUIPMENT_TYPE_CHOICES = [('Furnace', 'Furnace'), ('Air Conditioner', 'Air Conditioner'), ('Humidifier', 'Humidifier'), ('Coil', 'Coil'), ('Thermostat', 'Thermostat'), ('Tank Water Heater', 'Tank Water Heater'), ('Tankless Water Heater', 'Tankless Water Heater'), ('Water Softener', 'Water Softener'), ('Mini Split', 'Mini Split')]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='equipment')
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    warranty_expiration_date = models.DateField(null=True, blank=True)
    filter_size = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.get_equipment_type_display()} - {self.manufacturer} {self.model_number}"

class Part(models.Model):
    model_number = models.CharField(max_length=100, unique=True)
    part_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=100, blank=True)
    specs = models.JSONField(default=dict, blank=True)
    manual_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.part_name

# =================================================================
# Financial & Service Models
# =================================================================

class ServiceHistory(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='service_history')
    service_date = models.DateField()
    technician_name = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Service for {self.equipment} on {self.service_date}"

class Invoice(models.Model):
    STATUS_CHOICES = [('Paid', 'Paid'), ('Unpaid', 'Unpaid'), ('Overdue', 'Overdue'), ('Pending Payment', 'Pending Payment')]
    PAYMENT_METHOD_CHOICES = [('Credit Card', 'Credit Card'), ('Check', 'Check'), ('Cash', 'Cash'), ('Bank Loan', 'Bank Loan'), ('N/A', 'N/A')]
    service_history = models.ForeignKey(ServiceHistory, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='N/A')
    check_number = models.CharField(max_length=50, blank=True, null=True)
    is_estimate = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.id} for {self.client}"
        
class Note(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notes')
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.client} on {self.created_at.strftime('%Y-%m-%d')}"

class MaintenanceReminder(models.Model):
    STATUS_CHOICES = [('Scheduled', 'Scheduled'), ('Sent', 'Sent'), ('Completed', 'Completed')]
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='reminders')
    reminder_date = models.DateField()
    reminder_type = models.CharField(max_length=100, blank=True, help_text="e.g., 'Annual Summer Tune-Up'")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Scheduled')
    
    def __str__(self):
        return f"Reminder for {self.equipment} on {self.reminder_date}"
        
# =================================================================
# Employee & HR Models
# =================================================================

class TimeLog(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs')
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PTORequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')]
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pto_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

# =================================================================
# System & Utility Models
# =================================================================

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    service_history = models.ForeignKey(ServiceHistory, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)

    def __str__(self):
        return self.file.name

class Notification(models.Model):
    CHANNEL_CHOICES = [('sms', 'SMS'), ('email', 'Email')]
    STATUS_CHOICES = [('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    client_recipient = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    channel = models.CharField(max_length=5, choices=CHANNEL_CHOICES)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.CharField(max_length=50, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.action} at {self.timestamp}"
