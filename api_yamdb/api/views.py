from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
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
### Обратите внимание, что еще можно убрать в общий класс.

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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter
                       )
    ordering_filds = ('title_id')
    filterset_class = TitleFilter
### ГОТОВО Можно добавить возможность сортировки. Сортировать по всем полям не всегда нужна, ее можно ограничить.
    def get_serializer_class(self):
        if self.action in permissions.SAFE_METHODS: ### ХЗ ХЗ НАДО ЧЕКНУТь Можно проверять на "безопасный метод" SAFE_METHODS.
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
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()  # ГОТОВО
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )


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
        ### ГОТОВО Надо получать review не только по полю id, но и по полю title_id, чтобы быть уверенными в привязке. Тут и в perform_create. Лучше создать метод для получения отзыва и избавиться от дублирования.
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id', 'title_id')
        )
