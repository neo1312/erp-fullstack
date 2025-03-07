from rest_framework import viewsets
from .models import Marca 
from .serializers import MarcaSerializer 

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer


