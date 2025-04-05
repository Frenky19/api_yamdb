from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator

from api.validators import validate_year
from users.models import User
from utils.constants import (LIMIT_OF_SYMBOLS, NAME_LIMIT, MAX_SCORE,
                             MIN_SCORE)


class BaseSlugModel(models.Model):
    """Абстрактная модель для жанров и категорий."""

    name = models.CharField(verbose_name='Название',
                            max_length=NAME_LIMIT,
                            unique=True)
    slug = models.SlugField(verbose_name='Уникальный слаг', unique=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return Truncator(self.name).words(LIMIT_OF_SYMBOLS)


class Category(BaseSlugModel):
    """Модель категорий произведений (например, 'Фильмы', 'Книги')."""

    class Meta(BaseSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseSlugModel):
    """Модель жанров произведений (например, 'Фантастика', 'Драма')."""

    class Meta(BaseSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """
    Модель произведения (фильм, книга и т.д.).

    Attributes:
        name: Название произведения.
        year: Год выпуска с валидацией (не может быть будущим).
        category: Связь с категорией (может быть пустой).
        description: Краткое описание произведения (необязательное).
        genre: Связь M2M с жанрами.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_LIMIT,
        db_index=True
    )
    year = models.PositiveIntegerField(
        verbose_name='Год',
        validators=(validate_year,)
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = '%(class)ss'

    def __str__(self):
        """Возвращает ограниченное строковое представление произведения."""
        return Truncator(self.name).words(LIMIT_OF_SYMBOLS)


class BasePublicationModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['pub_date']

    def __str__(self):
        """Возвращает ограниченное строковое представление текста."""
        return Truncator(self.text).words(LIMIT_OF_SYMBOLS)


class Review(BasePublicationModel):
    """
    Модель отзывов на произведения.

    Один автор может оставить только один отзыв на произведение.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ),
        error_messages={'validators': f'Оценка от {MIN_SCORE} до {MAX_SCORE}!'}
    )

    class Meta(BasePublicationModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )
        ]


class Comment(BasePublicationModel):
    """
    Модель комментариев к отзывам.

    Attributes:
        review: Связанный отзыв (ForeignKey).
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta(BasePublicationModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'
