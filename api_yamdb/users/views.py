from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from api.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class SignupView(APIView):
    def post(self, request):
        # Логика регистрации и отправки confirmation code
        ...


class TokenView(APIView):
    def post(self, request):
        # Логика выдачи JWT токена
        ...
