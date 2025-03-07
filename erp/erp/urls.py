from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('crm.urls')),  # ✅ Correct way
    path('api/', include('SCM.urls')),  # ✅ Correct way
    
]

