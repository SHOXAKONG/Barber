from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import time
from django.db import models
from .roles import Roles

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    telegram_id = models.BigIntegerField(default=1001, unique=True)

    first_name = models.CharField("Ism / Имя", max_length=150, blank=True)

    phone_regex = RegexValidator(
        regex=r'^\+?998\d{9}$'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True,
                                    verbose_name="Telefon raqami / Телефонный номер")

    username = None

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name']

    objects = UserManager()

    name = models.CharField(max_length=255, blank=True, null=True)

    rating = models.FloatField(null=True, blank=True)

    photo = models.ImageField(upload_to='barber_images/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yxatdan o'tgan sana / Дата регистрации")

    roles = models.ManyToManyField(Roles)

    default_from_hour = models.TimeField(default=time(9, 0))  
    default_to_hour = models.TimeField(default=time(18, 0)) 

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    @property
    def is_not_client(self):
        staff_roles = {'Barber', 'Manager', 'Director'}
        return self.roles.filter(name__in=staff_roles).exists()
    
    def __str__(self):
        return f"{self.first_name} - {self.phone_number} - {self.telegram_id}"

    class Meta(AbstractUser.Meta):
        verbose_name = "Foydalanuvchi / Пользователь"
        verbose_name_plural = "Foydalanuvchilar / Пользователи"