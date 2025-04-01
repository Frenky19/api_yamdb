from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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
    TokenSerializer, UserSerializer, MeSerializer, SignupSerializer
)


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
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
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        """Получение и изменение данных своей учетной записи."""
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




# from rest_framework.generics import RetrieveUpdateAPIView
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from users.serializers import UserSerializer, SignupSerializer, TokenSerializer


# class UserView(RetrieveUpdateAPIView):
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user

#     def perform_update(self, serializer):
#         if 'role' in serializer.validated_data:
#             if not self.request.user.is_admin:
#                 del serializer.validated_data['role']
#         serializer.save()


# class SignupView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class TokenView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         serializer = TokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)
