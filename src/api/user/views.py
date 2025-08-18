import datetime
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer, UpdateRoleSerializer, RolesSerializer, UserUpdateSerializer
from src.apps.user.models import User, Roles
from src.apps.booking.models import WorkingHours
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Q

class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Registered Successfully"}, status=status.HTTP_201_CREATED)

class UsersViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ['add_role', 'remove_role']:
            return UpdateRoleSerializer
        elif self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path=r'by-role/(?P<role_id>[^/.]+)')
    def by_role(self, request, role_id=None):
        role_id = role_id
        role = get_object_or_404(Roles, id = role_id)
        if role.name == 'Client' or role.name=='BAN':
            queryset = User.objects.annotate(
                num_roles=Count('roles', distinct=True),
                total_bookings=Count('bookings', filter=Q(bookings__status='COMPLETED'), distinct=True)
                ).filter(roles__id=2).filter(
                    Q(num_roles=1) | (Q(num_roles=2) & Q(roles__id=5))
                ).distinct()
        else:
            queryset = User.objects.filter(roles__name = role.name)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path=r'add_role/(?P<phone_number>[^/.]+)')
    def add_role(self, request, phone_number=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, phone_number=phone_number)
        role = serializer.validated_data['role']

        if role.name.lower() == 'barber':
            from_hour = serializer.validated_data.get('default_from_hour') or user.default_from_hour
            to_hour = serializer.validated_data.get('default_to_hour') or user.default_to_hour

            WorkingHours.objects.filter(barber=user).delete()

            defaults = {"barber": user, "from_hour": from_hour, "to_hour": to_hour}
            WorkingHours.objects.bulk_create(
                [WorkingHours(weekday=i, **defaults) for i in range(7)]
            )

        user.roles.add(role)
        return Response({'status': 'Role added'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path=r'remove_role/(?P<phone_number>[^/.]+)')
    def remove_role(self, request, phone_number=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, phone_number=phone_number)
        role = serializer.validated_data.get('role')

        if role.name.lower() == 'barber':
            WorkingHours.objects.filter(barber=user).delete()

        user.roles.remove(role)
        return Response({'status': 'Role removed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='if_exists/(?P<telegram_id>[^/.]+)')
    def if_exists(self, request, telegram_id=None):
        user = get_object_or_404(User, telegram_id=telegram_id)
        return Response(UserSerializer(user).data)
    
# class UpdateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
#     queryset = User.objects.all()
#     lookup_field = 'telegram_id'

#     def get_object(self):
#         telegram_id = self.kwargs.get('telegram_id')
#         return User.objects.get(telegram_id=telegram_id)
        
#     def partial_update(self, request, *args, **kwargs):
#         return super().partial_update(request, *args, **kwargs)

#     def retrieve(self, request):
#         pass

class RolesViewSet(viewsets.GenericViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)