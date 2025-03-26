from rest_framework.views import APIView
from rest_framework.response import Response  # Make sure to import Response here
from .models import Provedor  # Import your provider model
from .serializers import ProviderSerializer

class ProviderList(APIView):
    def get(self, request):
        providers = Provedor.objects.all()
        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data)

