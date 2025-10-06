# api/filters.py

from django_filters import rest_framework as filters
from .models import Appointment, JobType

class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass

class AppointmentFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='end_time__date', lookup_expr='gte', label='Start Date')
    end_date = filters.DateFilter(field_name='start_time__date', lookup_expr='lte', label='End Date')
    technician_ids = NumberInFilter(field_name='technicians__id', lookup_expr='in', label='Technician IDs')
    job_type = filters.ModelChoiceFilter(queryset=JobType.objects.all(), label='Job Type')

    class Meta:
        model = Appointment
        fields = ['start_date', 'end_date', 'technician_ids', 'job_type']