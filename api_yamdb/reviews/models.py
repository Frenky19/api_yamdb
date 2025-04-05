from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator

from reviews.validators import validate_year
from users.models import User
from utils.constants import (LIMIT_OF_SYMBOLS, LONG_TEXT_LIMIT, MAX_SCORE,
                             MIN_SCORE)


class BaseSlugModel(models.Model):
    """Абстрактная модель для жанров и категорий."""
    name = models.CharField(max_length=LONG_TEXT_LIMIT, unique=True)
    slug = models.SlugField(unique=True)

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
    """Модель произведения (фильм, книга и т.д.).

    Attributes:
        name: Название произведения.
        year: Год выпуска с валидацией (не может быть будущим).
        category: Связь с категорией (может быть пустой).
        description: Краткое описание произведения (необязательное).
        genre: Связь M2M с жанрами.
    """

    name = models.CharField(
        'название',
        max_length=LONG_TEXT_LIMIT,
        db_index=True
    )
    year = models.PositiveIntegerField(
        'год',
        validators=(validate_year,)
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        'описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='жанр'
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

    text = models.CharField(
        max_length=LONG_TEXT_LIMIT,
        verbose_name='текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['pub_date']

    def __str__(self):
        """Возвращает ограниченное строковое представление текста."""
        return Truncator(self.text).words(LONG_TEXT_LIMIT)


class Review(BasePublicationModel):
    """Модель отзывов на произведения.

    Attributes:
        title: Связанное произведение (ForeignKey).
        score: Оценка от 1 до 10.

    Constraints:
        Один автор может оставить только один отзыв на произведение.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True
    )
    score = models.PositiveSmallIntegerField(
        'оценка',
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
    """Модель комментариев к отзывам.

    Attributes:
        review: Связанный отзыв (ForeignKey).
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='отзыв'
    )
    text = models.TextField('текст комментария',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta(BasePublicationModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'
