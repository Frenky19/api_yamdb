from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.filters import TitleFilter
from api.permissions import (AdminModeratorAuthorPermission,
                             IsAdminUserOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleReadSerializer, TitleWriteSerializer)
from reviews.models import Category, Genre, Review, Title


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

    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class CategoryViewSet(CustomModelViewSet):
    """
    API endpoint для работы с категориями произведений.

    Действия:
    - GET /categories/ — список всех категорий
    - GET /categories/{slug}/ — детализация категории
    - POST /categories/ — создание новой категории (только админ)
    - DELETE /categories/{slug}/ — удаление категории (только админ)

    Права доступа:
    - Чтение: доступно без токена
    - Запись: требуется права администратора
    - Удаление: требуется права администратора

    Параметры:
    - search: фильтрация по названию (регистронезависимый поиск)
    - lookup_field: slug (используется в URL вместо id)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CustomModelViewSet):
    """
    API endpoint для работы с жанрами произведений.

    Действия:
    - GET /genres/ — список всех жанров
    - GET /genres/{slug}/ — детализация жанра
    - POST /genres/ — создание нового жанра (только админ)
    - DELETE /genres/{slug}/ — удаление жанра (только админ)

    Права доступа:
    - Чтение: доступно без токена
    - Запись: требуется права администратора
    - Удаление: требуется права администратора

    Параметры:
    - search: фильтрация по названию (регистронезависимый поиск)
    - lookup_field: slug (используется в URL вместо id)
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    """
    API endpoint для работы с произведениями.

    Действия:
    - GET /titles/ — список всех произведений с рейтингом
    - GET /titles/{id}/ — детализация произведения
    - POST /titles/ — создание произведения (только админ)
    - PATCH /titles/{id}/ — частичное обновление (админ/модератор)
    - DELETE /titles/{id}/ — удаление произведения (только админ)

    Особенности:
    - PUT-запросы запрещены (только PATCH)
    - Рейтинг рассчитывается как среднее оценок отзывов
    - Используются разные сериализаторы для чтения и записи

    Права доступа:
    - Чтение: доступно без токена
    - Запись: требуется права администратора/модератора
    - Удаление: требуется права администратора
    """

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('rating')
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    ordering_fields = ('title_id',)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления отзывами на произведения.

    Действия:
    - GET /titles/{title_id}/reviews/ — список отзывов
    - POST /titles/{title_id}/reviews/ — создать отзыв (аутентиф. пользователи)
    - GET /titles/{title_id}/reviews/{id}/ — детализация отзыва
    - PATCH /titles/{title_id}/reviews/{id}/ — обновить отзыв
    - DELETE /titles/{title_id}/reviews/{id}/ — удалить отзыв

    Правила:
    - Один пользователь — один отзыв на произведение
    - Редактировать/удалять могут: автор, модератор или админ
    - PUT-запросы запрещены (только PATCH)

    Параметры:
    - title_id: ID произведения в URL
    """

    serializer_class = ReviewSerializer

    permission_classes = (IsAuthenticatedOrReadOnly,
                          AdminModeratorAuthorPermission)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint для управления комментариями к отзывам.

    Действия:
    - GET /titles/{title_id}/reviews/{review_id}/comments/ — список
        комментариев
    - POST /titles/{title_id}/reviews/{review_id}/comments/ — создать
        комментарий
    - PATCH /titles/{title_id}/reviews/{review_id}/comments/{id}/ — обновить
    - DELETE /titles/{title_id}/reviews/{review_id}/comments/{id}/ — удалить

    Правила:
    - Редактировать/удалять могут: автор, модератор или админ
    - PUT-запросы запрещены (только PATCH)
    - Привязка к отзыву через review_id в URL

    Параметры:
    - review_id: ID отзыва в URL
    - title_id: ID произведения в URL
    """

    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          AdminModeratorAuthorPermission)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
