from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/crm/', include('crm.urls')),  # CRM API
    path('api/scm/', include('SCM.urls')),  # SCM API
]
