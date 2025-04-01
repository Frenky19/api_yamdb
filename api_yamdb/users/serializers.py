from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from users.models import User
import secrets
from users.email import send_confirmation_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено')
        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.confirmation_code = secrets.token_urlsafe(6)
        user.save()
        try:
            send_confirmation_email(
                email=user.email,
                confirmation_code=user.confirmation_code
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()

        if not user or user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                'Введен неверный проверочный код или имя пользователя.'
            )
        return {
            'token': str(AccessToken.for_user(user))
        }
