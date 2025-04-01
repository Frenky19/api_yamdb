from django.urls import path
from users.views import SignupView, TokenObtainView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
]
