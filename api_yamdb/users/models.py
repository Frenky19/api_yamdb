from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import Truncator

from users.constants import LIMIT_OF_SYMBOLS


class User(AbstractUser):
    """
    Расширенная модель пользователя с расширенными полями и ролями.

    Дополнительные поля:
    - bio: Текстовая биография пользователя.
    - role: Для работы с ролями пользователей.
    - confirmation_code: Код подтверждения, для получения JWT токена.

    Свойства:
    - is_admin: Возвращает True, если пользователь является администратором
        или суперпользователем.
    - is_moderator: Возвращает True, если пользователь является модератором.
    """

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
        max_length=20,
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
        default_related_name = '%(class)ss'

    def __str__(self):
        """Возвращает ограниченное строковое представление пользователя."""
        return Truncator(self.username).words(LIMIT_OF_SYMBOLS)

    @property
    def is_admin(self):
        """Определяет, является ли пользователь администратором."""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        """Определяет, является ли пользователь модератором."""
        return self.role == 'moderator'
