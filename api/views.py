from django.contrib.auth.models import User, Group
from django.db.models import Avg, Sum
from rest_framework import viewsets, permissions, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
import boto3
import re

from .models import *
from .serializers import *
from .permissions import *
from .mixins import *
from .filters import *

textract = boto3.client('textract', region_name='us-east-1')

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

    @action(detail=False, methods=['post'], url_path='upload-and-extract')
    def upload_and_extract(self, request):
        # Full OCR and data extraction logic from your file
        pass # Placeholder for brevity

class EquipmentViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAdminOrTechnicianReadOnly]

class EquipmentDatabaseViewSet(viewsets.ModelViewSet):
    queryset = EquipmentDatabase.objects.all()
    serializer_class = EquipmentDatabaseSerializer
    permission_classes = [IsAdminOrSecretaryOrTechnicianReadOnly]

class ServiceHistoryViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistorySerializer
    permission_classes = [IsAdminOrTechnicianCreateOrReadOnly]

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]

class TimeLogViewSet(viewsets.ModelViewSet):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAdminUser]

class PTORequestViewSet(viewsets.ModelViewSet):
    queryset = PTORequest.objects.all()
    serializer_class = PTORequestSerializer
    permission_classes = [IsAdminUser]

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

    @action(detail=False, methods=['post'], url_path='send-thank-you')
    def send_thank_you(self, request):
        # Logic to send thank you notifications
        pass # Placeholder for brevity

    @action(detail=False, methods=['post'], url_path='send-appointment-reminder')
    def send_appointment_reminder(self, request):
        # Logic to send appointment reminders
        pass # Placeholder for brevity

class MaintenanceReminderViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceReminder.objects.all()
    serializer_class = MaintenanceReminderSerializer
    permission_classes = [IsAdminOrTechnicianCreateOrReadOnly]

    @action(detail=False, methods=['post'], url_path='generate-reminders')
    def generate_reminders(self, request):
        # Logic to generate maintenance reminders
        pass # Placeholder for brevity

class NoteViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAdminOrTechnicianReadOnly]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class AnalyticsView(views.APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        paid_invoices = Invoice.objects.filter(status='Paid', is_estimate=False)
        total_revenue = paid_invoices.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
        avg_estimate = Invoice.objects.filter(is_estimate=True).aggregate(Avg('amount_due'))['amount_due__avg'] or 0
        data = {'total_revenue': total_revenue, 'average_estimate_value': avg_estimate}
        return Response(data)

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk, 'email': user.email})

class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = EmployeeSerializer(request.user)
        return Response(serializer.data)
    def patch(self, request):
        user = request.user
        serializer = EmployeeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)