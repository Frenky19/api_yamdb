from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


### Готово Это не миксин, это полноценный вьюсет. Этот класс лежит сейчас в модуле с несоответствующим именем. Можно переместить во вью или создать модуль с более подходящим именем.
### Оставил тут что бы не засорять views :)
class CustomModelViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    """
    Набор миксинов для создания, списка и удаления моделей.

    Этот класс объединяет функции создания, списка и удаления моделей
    в одном наборе представлений. Он наследуется от:
    - CreateModelMixin: Обеспечивает создание новых объектов модели.
    - ListModelMixin: Обеспечивает получение списка объектов модели.
    - DestroyModelMixin: Обеспечивает удаление объектов модели.
    - GenericViewSet: Базовый класс представлений.

    Методы:
    - create: Обработка создания нового объекта модели.
    - list: Обработка получения списка объектов модели.
    - destroy: Обработка удаления объекта модели.
    """
