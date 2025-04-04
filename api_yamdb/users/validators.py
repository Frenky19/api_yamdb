from django.core.exceptions import ValidationError

from users.constants import FORBIDDEN_USERNAME


def validate_username_not_me(value):
    """Запрещает использование имени 'me'."""
    if value == FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Использовать имя {FORBIDDEN_USERNAME}'
            'в качестве логина запрещено.'
        )
