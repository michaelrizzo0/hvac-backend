# api/admin.py
from django.contrib import admin
from .models import (
    Client, UserProfile, JobType, Appointment, Equipment, Part,
    ServiceHistory, Invoice, TimeLog, PTORequest, Attachment,
    Notification, AuditLog
)

# Register all your models here to make them visible in the admin panel
admin.site.register(Client)
admin.site.register(UserProfile)
admin.site.register(JobType)
admin.site.register(Appointment)
admin.site.register(Equipment)
admin.site.register(Part)
admin.site.register(ServiceHistory)
admin.site.register(Invoice)
admin.site.register(TimeLog)
admin.site.register(PTORequest)
admin.site.register(Attachment)
admin.site.register(Notification)
admin.site.register(AuditLog)
