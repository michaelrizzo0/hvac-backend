# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Client, UserProfile, JobType, Equipment, ServiceHistory, Note, Invoice,
    MaintenanceReminder, Part, TimeLog, PTORequest, Attachment, Notification, AuditLog,
    Appointment, EquipmentDatabase
)

# =================================================================
# User & Employee Serializers
# =================================================================
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('color', 'phone', 'address', 'is_active')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)

class EmployeeSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'profile', 'groups')

class EquipmentDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentDatabase
        fields = '__all__'

# =================================================================
# Part & HR Serializers
# =================================================================
class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'

class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'

class PTORequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTORequest
        fields = '__all__'

# =================================================================
# Core App Serializers
# =================================================================

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'

class ServiceHistorySerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True) # Added nested invoices
    class Meta:
        model = ServiceHistory
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    service_history = ServiceHistorySerializer(many=True, read_only=True)
    class Meta:
        model = Equipment
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    notes = serializers.StringRelatedField(many=True, read_only=True) # Added for convenience
    class Meta:
        model = Client
        fields = '__all__'

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = '__all__'

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class MaintenanceReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceReminder
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    technicians_details = EmployeeSerializer(source='technicians', many=True, read_only=True)
    client_details = ClientSerializer(source='client', read_only=True) # Added for convenience
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        start_time = data.get('start_time') or (self.instance and self.instance.start_time)
        end_time = data.get('end_time') or (self.instance and self.instance.end_time)
        technicians = data.get('technicians')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Appointment end time must be after start time.")

        if technicians:
            for technician in technicians:
                conflicting_appointments = Appointment.objects.filter(
                    technicians=technician,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                if self.instance:
                    conflicting_appointments = conflicting_appointments.exclude(pk=self.instance.pk)
                if conflicting_appointments.exists():
                    raise serializers.ValidationError(
                        f"Technician {technician.username} is already booked during this time."
                    )
        return data