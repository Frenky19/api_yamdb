from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from users.constants import (ALLOWED_SYMBOLS_FOR_USERNAME,
                             EMAIL_LENGTH,
                             USERNAME_LENGTH)
from users.models import User
from users.validators import validate_username_not_me


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.

    Используется для сериализации данных пользователя, включая поля:
    username, email, first_name, last_name, bio и role.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and not request.user.is_admin:
            self.fields['role'].read_only = True


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей, отправки кода подтверждения.

    Обрабатывает валидацию email и username:
    - Проверяет соответствие username паттерну ALLOWED_SYMBOLS_FOR_USERNAME
    - Запрещает использование username 'me'
    - Контролирует уникальность связки email/username

    Методы:
    - validate: Кастомная проверка на конфликт email/username с существующими
        пользователями
    - create: Создает или обновляет пользователя, генерирует код подтверждения
    - send_confirmation_email: Отправляет код на email пользователя

    Исключения:
    - ValidationError: При конфликте данных или ошибке отправки email
    """

    email = serializers.EmailField(max_length=EMAIL_LENGTH)
    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        validators=[
            RegexValidator(regex=ALLOWED_SYMBOLS_FOR_USERNAME),
            validate_username_not_me
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        """Проверяет уникальность связки email/username.

        Args:
            data (dict): Входные данные (email и username)

        Returns:
            dict: Валидированные данные

        Raises:
            ValidationError: Если:
                - email занят другим username
                - username занят другим email
        """
        email = data.get('email')
        username = data.get('username')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.username != username:
                raise serializers.ValidationError(
                    {'email': 'Email уже занят'}
                )
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError(
                    {'username': 'Username уже занят'}
                )
        return data

    def create(self, validated_data):
        """Создает или обновляет пользователя.

        Логика:
        1. Ищет пользователя по email и username
        2. Если не найден - создает нового с is_active=False
        3. Генерирует новый confirmation_code
        4. Отправляет код на email

        Args:
            validated_data (dict): Валидные данные (email, username)

        Returns:
            User: Созданный/обновленный пользователь
        """
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            defaults={'is_active': False}
        )
        user.confirmation_code = default_token_generator.make_token(user)
        user.save(update_fields=['confirmation_code'])
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        """Отправляет письмо с кодом подтверждения.

        Args:
            user (User): Объект пользователя для отправки

        Raises:
            ValidationError: При ошибке отправки email
        """
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена аутентификации.

    Требует поля username и confirmation_code. Проверяет, что confirmation_code
    соответствует коду, хранящемуся для пользователя, и при успешной валидации
    возвращает токен и username.
    """

    username = serializers.CharField(max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Основная логика валидации кода подтверждения."""
        user = get_object_or_404(User, username=data['username'])
        confirmation_code = data.get('confirmation_code')
        if not confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Код подтверждения обязателен.'}
            )
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        return {
            'token': str(AccessToken.for_user(user)),
            'username': user.username,
        }
