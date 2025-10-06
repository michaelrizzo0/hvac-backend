# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()

# Core Business Logic
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'equipment-database', views.EquipmentDatabaseViewSet, basename='equipmentdatabase')
router.register(r'service-history', views.ServiceHistoryViewSet, basename='servicehistory')

# Employee & HR
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'time-logs', views.TimeLogViewSet, basename='timelog')
router.register(r'pto-requests', views.PTORequestViewSet, basename='ptorequest')

# Parts & Utility
router.register(r'parts', views.PartViewSet, basename='part')
router.register(r'job-types', views.JobTypeViewSet, basename='jobtype')
router.register(r'attachments', views.AttachmentViewSet, basename='attachment')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

# Added Missing Routes
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'reminders', views.MaintenanceReminderViewSet, basename='reminder')
router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')
router.register(r'user-profiles', views.UserProfileViewSet, basename='userprofile')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    # Added the path for the "Me" view
    path('me/', views.MeView.as_view(), name='me'),
]