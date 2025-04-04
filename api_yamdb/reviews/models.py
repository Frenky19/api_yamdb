from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator

from reviews.validators import validate_year
from users.constants import LIMIT_OF_SYMBOLS, REVIEW_COMMENT_TEXT_LIMIT,  MIN_SCORE, MAX_SCORE
from users.models import User


class Category(models.Model):
    """Модель категорий произведений (например, 'Фильмы', 'Книги').

    Attributes:
        name: Название категории (уникальное).
        slug: Уникальный идентификатор категории для URL.
    """

    name = models.CharField(max_length=256, unique=True) ### Все длины полей выносим в константы. Все константы лучше собрать в одном файле проекта.
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает ограниченное строковое представление категории."""
        return Truncator(self.name).words(LIMIT_OF_SYMBOLS)
### Принцип DRY. В моделях категорий и жанров одинаковые строки, их лучше вынести в абстрактную модель и наследоваться от нее.
### В Meta абстрактного класса стоит добавить сортировку по "имени". Метод __str__ также размещаем в абстрактной. 


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
    year = models.IntegerField( ### Неверно подобран тип поля, есть поле с меньшим возможным максимальным числом.
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


class BaseModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    text = models.CharField(
        max_length=REVIEW_COMMENT_TEXT_LIMIT,
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
        return Truncator(self.text).words(REVIEW_COMMENT_TEXT_LIMIT)


class Review(BaseModel):
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
    score = models.PositiveSmallIntegerField( ###Готово Тут лучше использовать PositiveSmallIntegerField. Будет занимать меньше места в БД.
        'оценка',
        validators=(
            MinValueValidator(MIN_SCORE), ### Готово Значения контролируем константами.
            MaxValueValidator(MAX_SCORE)
        ),
        error_messages={'validators': f'Оценка от {MIN_SCORE} до {MAX_SCORE}!'}
    )
    ### Если будем менять значение константы, то сообщение уже не будет соответствовать
    ### действительности, его придется тоже править, вот тут как раз и пример
    ### преимущества применения констант(поможет f-строка или метод format).
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )]


class Comment(BaseModel):
    """Модель комментариев к отзывам.

    Attributes:
        review: Связанный отзыв (ForeignKey).
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = '%(class)ss'

#ГОТОВОПринцип DRY. В моделях отзывов и комментариев одинаковые строки, их лучше вынести в абстрактную
#ГОТОВО модель и наследоваться от нее. В Meta абстрактного класса стоит добавить сортировку. Метод __str__ также размещаем в абстрактной.
#https://docs.djangoproject.com/en/3.2/topics/db/models/#meta-inheritance.