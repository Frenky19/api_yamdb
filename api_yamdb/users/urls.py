from django.urls import path

from users.views import SignupView, TokenObtainView

urlpatterns = [
    path(
        'signup/',
        SignupView.as_view(),
        name='signup',
        doc=(
            'Регистрация нового пользователя/'
            'получение кода подтверждения для зарегестрированного'
        )
    ),
    path(
        'token/',
        TokenObtainView.as_view(),
        name='token_obtain',
        doc="Получение JWT токена"
    ),
]
