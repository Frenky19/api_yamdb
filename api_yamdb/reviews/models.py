from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator

from reviews.validators import validate_year
from users.constants import LIMIT_OF_SYMBOLS
from users.models import User


class Category(models.Model):
    """Модель категорий произведений (например, 'Фильмы', 'Книги').

    Attributes:
        name: Название категории (уникальное).
        slug: Уникальный идентификатор категории для URL.
    """

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        default_related_name = '%(class)ss'

    def __str__(self):
        """Возвращает ограниченное строковое представление категории."""
        return Truncator(self.name).words(LIMIT_OF_SYMBOLS)


class Genre(models.Model):
    """Модель жанров произведений (например, 'Фантастика', 'Драма').

    Attributes:
        name: Название жанра (уникальное).
        slug: Уникальный идентификатор жанра для URL.
    """

    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        default_related_name = '%(class)ss'

    def __str__(self):
        """Возвращает ограниченное строковое представление жанра."""
        return Truncator(self.name).words(LIMIT_OF_SYMBOLS)


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
        max_length=200,
        db_index=True
    )
    year = models.IntegerField(
        'год',
        validators=(validate_year, )
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
        max_length=255,
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


class Review(models.Model):
    """Модель отзывов на произведения.

    Attributes:
        title: Связанное произведение (ForeignKey).
        text: Текст отзыва (до 200 символов).
        author: Автор отзыва (пользователь).
        score: Оценка от 1 до 10.
        pub_date: Дата публикации (автоматически добавляется).

    Constraints:
        Один автор может оставить только один отзыв на произведение.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )
    text = models.CharField(
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True
    )
    score = models.IntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        """Возвращает ограниченное строковое представление отзыва."""
        return Truncator(self.text).words(LIMIT_OF_SYMBOLS)


class Comment(models.Model):
    """Модель комментариев к отзывам.

    Attributes:
        review: Связанный отзыв (ForeignKey).
        text: Текст комментария (до 200 символов).
        author: Автор комментария (пользователь).
        pub_date: Дата публикации (автоматически добавляется).
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='отзыв'
    )
    text = models.CharField(
        'текст комментария',
        max_length=200
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
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'
        ordering = ["pub_date"]

    def __str__(self):
        """Возвращает ограниченное строковое представление комментария."""
        return Truncator(self.text).words(LIMIT_OF_SYMBOLS)
