from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя', max_length=50, blank=False, unique=True)
    email = models.EmailField('Email', blank=False, unique=True,
                              validators=[validators.validate_email])
    confirmation_code = models.CharField('Код подтверждения', max_length=30,
                                         blank=True, null=True)
    first_name = models.CharField(
        max_length=150, null=True, blank=True)
    last_name = models.CharField(
        max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.is_active = True
        super().save(*args, **kwargs)
