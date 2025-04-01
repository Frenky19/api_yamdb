from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import Truncator
from users.constants import LIMIT_OF_SYMBOLS


class User(AbstractUser):
    """Модель пользователя с расширенными полями и ролями."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в имени пользователя.'
            )
        ]
    )
    email = models.EmailField('Электронная почта', max_length=254, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=100,
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=16,
        blank=True
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return Truncator(self.username).words(LIMIT_OF_SYMBOLS)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
