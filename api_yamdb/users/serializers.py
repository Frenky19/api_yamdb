from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from users.models import User
from rest_framework_simplejwt.tokens import AccessToken


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
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
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )
        return {
            'token': str(AccessToken.for_user(user)),
            'username': user.username,
        }


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio'
        )
        read_only_fields = ('role',)



# from rest_framework import serializers
# from rest_framework_simplejwt.tokens import AccessToken
# from django.contrib.auth import authenticate
# from users.models import User
# import secrets
# from django.core.mail import send_mail


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'username', 'email', 'first_name', 'last_name', 'bio', 'role'
#         )


# class SignupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('email', 'username')

#     def validate_username(self, value):
#         if value.lower() == 'me':
#             raise serializers.ValidationError('Имя "me" запрещено')
#         return value

#     def create(self, validated_data):
#         user = User.objects.create(**validated_data)
#         user.confirmation_code = secrets.token_urlsafe(16)
#         user.save()
#         send_mail(
#             subject='Код подтверждения Yamdb',
#             message=f'Ваш код подтверждения: {user.confirmation_code}',
#             from_email=None,  # Значение берется из DEFAULT_FROM_EMAIL
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
#         return user


# class TokenSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     confirmation_code = serializers.CharField()

#     def validate(self, data):
#         user = User.objects.filter(username=data['username']).first()

#         if not user or user.confirmation_code != data['confirmation_code']:
#             raise serializers.ValidationError(
#                 'Введен неверный проверочный код или имя пользователя.'
#             )
#         return {
#             'token': str(AccessToken.for_user(user))
#         }
