from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from src.apps.breakes.models import Break
from .serializers import BreakSerializer


class BreakViewSet(viewsets.GenericViewSet):
    queryset = Break.objects.all()
    serializer_class = BreakSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Break Saved Successfully"}, status=status.HTTP_201_CREATED
        )

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="barber_detail/(?P<barber_id>[^/.]+)")
    def barber_detail(self, request, pk=None, barber_id=None):
        breaks = Break.objects.filter(id=pk, barber_id=barber_id, end_time__gt=timezone.now()).first()
        if breaks:
            serializer = self.get_serializer(breaks)
            return Response(serializer.data)
        return Response({"message" : "Break Topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        breaks = self.get_object()
        serializer = self.get_serializer(breaks, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Break Updated Successfully"})

    def destroy(self, request, pk=None, ):
        breaks = self.get_object()
        breaks.delete()

        return Response(
            {"message": "Break Deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(methods=['get'], detail=False, url_path='get_breaks_by_barber_id/(?P<barber_id>\d+)')
    def get_breaks_by_barber_id(self, request, barber_id=None):
        breaks = Break.objects.filter(barber=barber_id, end_time__gt=timezone.now())

        if not breaks.exists():
            return Response({"message": "Breaklar topilmadi"})

        serializer = self.get_serializer(breaks, many=True)
        return Response(serializer.data)
