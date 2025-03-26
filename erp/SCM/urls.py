from django.urls import path
from .views import ProviderList  # Ensure you import the correct view

urlpatterns = [
    path('providers/', ProviderList.as_view(), name='provider-list'),
]

