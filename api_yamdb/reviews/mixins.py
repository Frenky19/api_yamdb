from rest_framework import status
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ModelMixinSet(
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
    pass


class PUTNotAllowedMixin:
    """
    Миксин для блокировки метода PUT в обновлении объектов.

    Методы:
        update: Блокирует обновление объекта методом PUT и возвращает
            ошибку 405 Method Not Allowed.
        partial_update: Делает частичное обновление объекта.
    """
    def update(self, request, *args, **kwargs):
        """
        Обрабатывает запросы на обновление объекта.

        Параметры:
            request (Request): Объект HTTP-запроса
            *args: Аргументы
            **kwargs: Именованные аргументы

        Возвращает:
            Response:
                - 405 Method Not Allowed для PUT-запросов
                - Стандартный ответ DRF для других методов
        """
        if request.method == 'PUT':
            return Response(
                {'error': 'Method not allowed'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Обрабатывает PATCH-запросы для частичного обновления объекта."""
        return super().partial_update(request, *args, **kwargs)
