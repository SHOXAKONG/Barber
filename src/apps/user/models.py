from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


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


class UserLang(models.TextChoices):
    UZ = ('uz', 'Uz')
    RU = ('ru', 'Ru')
    ENG = ('eng', 'Eng')


class User(AbstractUser):
    telegram_id = models.BigIntegerField(default=1000, unique=True)
    user_lang = models.CharField(max_length=10, choices=UserLang.choices, default=UserLang.UZ)

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

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yxatdan o'tgan sana / Дата регистрации")

    def __str__(self):
        return f"{self.first_name} - {self.phone_number} - {self.telegram_id}"

    class Meta(AbstractUser.Meta):
        verbose_name = "Foydalanuvchi / Пользователь"
        verbose_name_plural = "Foydalanuvchilar / Пользователи"

