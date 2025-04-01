from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900)])
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )
    # Поле рейтинга (вотчина Джамала:)
    rating = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для отзывов на произведения."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        unique_together = ('title', 'user')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = '%(class)ss'


class Comment(models.Model):
    """Модель для комментариев к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'
