from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """
    Проверяет, что указанный год не превышает текущий.

    Валидатор используется для проверки корректности года в различных моделях
    (например, для года выпуска произведений, публикаций и т.д.).

    Args:
        value (int): Проверяемое значение года.

    Raises:
        ValidationError: Если переданный год больше текущего.

    Returns:
        None: Функция не возвращает значение в случае успешной валидации.
    """
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'{value} не может быть больше {now}'
        )
