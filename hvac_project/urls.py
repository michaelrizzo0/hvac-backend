# hvac_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from api.views import CustomAuthToken

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Use the new, custom token view
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
]