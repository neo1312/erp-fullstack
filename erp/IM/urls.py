from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarcaViewSet

router = DefaultRouter()
router.register(r'marcas', MarcaViewSet)

urlpatterns = [
    path('', include(router.urls)),  # ✅ Correct
]
