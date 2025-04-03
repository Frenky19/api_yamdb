from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response


def send_confirmation_email(user, confirmation_code):
    """Вспомогательная функция для отправки кода подтверждения."""
    try:
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        error_message = (
            str(e)
            if settings.DEBUG
            else 'Не удалось отправить email'
        )
        return Response(
            {'error': error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
