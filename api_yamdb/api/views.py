from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from reviews.filters import TitleFilter
from reviews.mixins import ModelMixinSet, PUTNotAllowedMixin
from reviews.models import Category, Genre, Review, Title
from reviews.serializers import (CategorySerializer, CommentSerializer,
                                 GenreSerializer, ReviewSerializer,
                                 TitleReadSerializer, TitleWriteSerializer)
from users.permissions import (AdminModeratorAuthorPermission,
                               IsAdminUserOrReadOnly)


class CategoryViewSet(ModelMixinSet):
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
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
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
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(PUTNotAllowedMixin, ModelViewSet):
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
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(PUTNotAllowedMixin, viewsets.ModelViewSet):
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
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(PUTNotAllowedMixin, viewsets.ModelViewSet):
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
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
