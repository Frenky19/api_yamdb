from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


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


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя.

    Выполняет валидацию полей email и username:
    - email должен быть уникальным;
    - username должен быть уникальным, соответствовать шаблону и не быть
        равным 'me'.
    """

    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с таким email уже существует.'
        )]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким username уже существует.'
            ),
            RegexValidator(regex=r'^[\w.@+-]+\Z')
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена аутентификации.

    Требует поля username и confirmation_code. Проверяет, что confirmation_code
    соответствует коду, хранящемуся для пользователя, и при успешной валидации
    возвращает токен и username.
    """

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
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


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования профиля аутентифицированного юзера.

    Позволяет просматривать и редактировать поля: username, email, first_name,
    last_name и bio.
    Поле role не включено и не может быть изменено через этот сериализатор.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio'
        )
        read_only_fields = ('role',)
