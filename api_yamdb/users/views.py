from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from users.permissions import IsAdmin
from users.serializers import (
    MeSerializer, SignupSerializer, TokenSerializer, UserSerializer
)
from users.service import send_confirmation_email


class SignupView(APIView):
    """
    Представление для регистрации пользователей и отправки кода подтверждения.

    Разрешает неаутентифицированный доступ. При регистрации:
    - Если пользователь с указанными username/email существует: генерирует
        новый код подтверждения.
    - Если пользователь новый: создает запись пользователя и генерирует код
        потдверждения.
    - Во всех случаях отправляет код подтверждения на email.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Обрабатывает POST-запрос с данными регистрации.

        Параметры запроса:
        - username (обязательный)
        - email (обязательный)

        Возвращает:
        - 200 OK с username/email при успешной отправке кода
        - 500 при ошибке отправки email
        - 400 при невалидных данных
        """
        serializer = SignupSerializer(data=request.data)
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            user = get_object_or_404(User, username=username, email=email)
            confirmation_code = default_token_generator.make_token(user)
            user.confirmation_code = confirmation_code
            user.save()
            response = send_confirmation_email(user, confirmation_code)
            if response:
                return response
            return Response(
                {"email": email, "username": username},
                status=status.HTTP_200_OK
            )
        serializer.is_valid(raise_exception=True)
        user = User.objects.create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email']
        )
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        response = send_confirmation_email(user, confirmation_code)
        if response:
            return response
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    """
    Представление для получения JWT токена после верификации confirmation_code.

    Разрешает неаутентифицированный доступ. Проверяет соответствие:
    - username пользователя
    - кода подтверждения из email
    При успехе возвращает JWT токен для аутентификации.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Проверяет код подтверждения и выдает токен доступа.

        Параметры запроса:
        - username (обязательный)
        - confirmation_code (обязательный)

        Возвращает:
        - 200 OK с JWT токеном при успешной проверке
        - 400 при неверном коде или отсутствии пользователя
        - 404 при отсутствии пользователя в бд
        """
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if not default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            return Response(
                {'confirmation_code': 'Неверный код подтверждения.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями через API.

    Требует прав администратора для операций:
    - Просмотр списка/детализации
    - Создание/изменение/удаление пользователей

    Поддерживает:
    - Поиск по username (параметр search)
    - Пагинацию
    - Кастомный эндпоинт /me/ для личных данных
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        """
        Эндпоинт для работы с данными текущего пользователя.

        GET:
        - Возвращает данные аутентифицированного пользователя

        PATCH:
        - Позволяет частичное обновление данных пользователя
        - Запрещает изменение ролей и других привилегированных полей
        - Валидирует входные данные через MeSerializer
        """
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MeSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
