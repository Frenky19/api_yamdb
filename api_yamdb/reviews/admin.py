from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административная панель для модели Review."""

    list_display = (
        'title',
        'text',
        'author',
        'score',
    )
    search_fields = ('pub_date',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
### Можем воспользоваться admin.site.empty_value_display и задать значение общее для всех моделей. Таким образом мы избежим дублирования кода, и в одном месте сможем менять значение.

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Административная панель для модели Comment."""

    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('review',) ### Попробуйте в поиске что-нибудь найти, получите ошибку. Нужно дописать через двойное подчеркивание по какому полю стоит искать.
    list_filter = ('review',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административная панель для управления категориями."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Административная панель для управления жанрами."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Административная панель для управления произведениями."""

    list_display = (
        'name',
        'year',
        'category',
        'description',
    )
    search_fields = ('name', 'year', 'category__name', 'genre__name')
    list_filter = ('category', 'genre')
    filter_horizontal = ('genre',)
    empty_value_display = '-пусто-'
### Для произведений желательна возможность редактировать категории прямо в листе произведений.
# Кроме того нужно вывести список жанров через запятую в листе произведений (для этого придется написать метод).