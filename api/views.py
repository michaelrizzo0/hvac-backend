from django.contrib.auth.models import User, Group
from django.db.models import Avg, Sum
from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import (
    Client, UserProfile, JobType, Equipment, ServiceHistory, Note, Invoice,
    MaintenanceReminder, Part, TimeLog, PTORequest, Attachment, Notification, AuditLog,
    Appointment
)
from .serializers import (
    ClientSerializer, UserProfileSerializer, JobTypeSerializer, EquipmentSerializer,
    ServiceHistorySerializer, NoteSerializer, InvoiceSerializer, MaintenanceReminderSerializer,
    PartSerializer, TimeLogSerializer, PTORequestSerializer, AttachmentSerializer,
    NotificationSerializer, AuditLogSerializer, AppointmentSerializer, EmployeeSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrTechnicianReadOnly, IsAdminOrTechnicianCreateOrReadOnly,
    IsAdminOrSecretaryOrTechnicianReadOnly, IsAdminOrSecretaryOrTechnicianCreateOrReadOnly
)
from .mixins import AuditLoggingMixin
from .filters import AppointmentFilter


# =================================================================
# Core Business Logic ViewSets
# =================================================================

class ClientViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-created_at')
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianReadOnly]

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianReadOnly]
    filterset_class = AppointmentFilter

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name__in=['Admin', 'Secretary']).exists() or user.is_superuser:
            return Appointment.objects.all()
        elif user.groups.filter(name='Technician').exists():
            return Appointment.objects.filter(technicians=user)
        return Appointment.objects.none()

class InvoiceViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAdminUser]

class EquipmentViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAdminOrTechnicianReadOnly]

class ServiceHistoryViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistorySerializer
    permission_classes = [IsAdminOrTechnicianCreateOrReadOnly]

# =================================================================
# Employee & HR ViewSets
# =================================================================

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]

class TimeLogViewSet(viewsets.ModelViewSet):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAdminUser] # Or more granular permissions

class PTORequestViewSet(viewsets.ModelViewSet):
    queryset = PTORequest.objects.all()
    serializer_class = PTORequestSerializer
    permission_classes = [IsAdminUser] # Or more granular permissions

# =================================================================
# Parts & Utility ViewSets
# =================================================================

class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianReadOnly]

class JobTypeViewSet(viewsets.ModelViewSet):
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianReadOnly]

class AttachmentViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianCreateOrReadOnly]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]

# =================================================================
# System & Auth Views
# =================================================================

class AnalyticsView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        paid_invoices = Invoice.objects.filter(status='Paid', is_estimate=False)
        total_revenue = paid_invoices.aggregate(Sum('amount_due'))['amount_due__sum'] or 0

        avg_estimate = Invoice.objects.filter(is_estimate=True).aggregate(Avg('amount_due'))['amount_due__avg'] or 0

        data = {
            'total_revenue': total_revenue,
            'average_estimate_value': avg_estimate,
            # Add more analytics queries as needed
        }
        return Response(data)

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# Note: TechnicianViewSet is now covered by EmployeeViewSet
# Note: Other viewsets like Note, MaintenanceReminder, AuditLog, UserProfile can be added back if needed,
# but are omitted for brevity to focus on the new core logic.