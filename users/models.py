from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Создаёт и сохраняет пользователя с указанным email и паролем."""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт и сохраняет суперпользователя с указанным email и паролем."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями.

    Атрибуты:
        email (EmailField): Уникальный email, используемый в качестве логина.
        first_name (CharField): Имя пользователя.
        last_name (CharField): Фамилия пользователя.
        avatar (ImageField): Аватар пользователя. Загружается в 'users/avatars/'.
        is_active (BooleanField): Активность пользователя (вместо удаления).
    """

    username = None
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Введите email")
    first_name = models.CharField(
        max_length=50, verbose_name="Имя", help_text="Введите ваше Имя", blank=True, null=True
    )
    last_name = models.CharField(
        max_length=50, verbose_name="Фамилия", help_text="Введите ваше Фамилию", blank=True, null=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Активность")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
