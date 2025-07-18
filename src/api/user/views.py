from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer, LanguageSerializer
from src.apps.user.models import User


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Registered Successfully"}, status=status.HTTP_201_CREATED)


class UsersViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='is_staff')
    def is_staff(self, request):
        queryset = User.objects.filter(is_staff=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='client')
    def client(self, request):
        queryset = User.objects.filter(is_staff=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UpdateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = LanguageSerializer
    queryset = User.objects.all()
    lookup_field = 'telegram_id'

    def get_object(self):
        telegram_id = self.kwargs.get('telegram_id')
        try:
            return User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise NotFound(detail="User with this telegram_id not found.")

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def retrieve(self, request):
        pass


