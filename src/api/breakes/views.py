from rest_framework import viewsets, permissions
from src.apps.breakes.models import Break
from .serializers import BreakSerializer

class BreakViewSet(viewsets.ModelViewSet):
    queryset = Break.objects.all()
    serializer_class = BreakSerializer