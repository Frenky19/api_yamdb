from django.conf import settings
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAdmin
from users.models import User
from users.serializers import SignupSerializer, TokenSerializer, UserSerializer


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
        - 500 при ошибке на стороне сервера
        - 400 при невалидных данных
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(
                {
                    'email': serializer.data['email'],
                    'username': serializer.data['username']
                },
                status=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            error_message = (
                str(e) if settings.DEBUG
                else 'Ошибка со стороны клиента'
            )
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            error_message = (
                str(e) if settings.DEBUG
                else 'Ошибка на сервере'
            )
            return Response(
                {'error': error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TokenObtainView(APIView):
    """
    Представление для получения JWT токена после верификации confirmation_code.

    Логика работы:
    1. Принимает username и confirmation_code
    2. Валидирует данные через TokenSerializer
    3. Возвращает JWT токен при успехе
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
        """
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
        - Валидирует входные данные через UserSerializer
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
