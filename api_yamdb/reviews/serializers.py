from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Предоставляет сериализацию и десериализацию объектов категорий.
    Используется для отображения и создания категорий в API.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Предоставляет сериализацию и десериализацию объектов жанров.
    Используется для отображения и создания жанров в API.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Обеспечивает создание и получение отзывов для произведений.
    Реализует проверку оценки (от 0 до 10) и уникальности отзыва
    от одного пользователя для каждого произведения.
    """

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        """
        Проверяет, что оценка находится в диапазоне от 0 до 10.

        Args:
            value (int): Значение оценки

        Returns:
            int: Корректное значение оценки

        Raises:
            ValidationError: Если оценка выходит за пределы диапазона
        """
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        """
        Проверяет, что пользователь не оставит более 1 отзыва на произведение.

        Args:
            data (dict): Данные для валидации

        Returns:
            dict: Проверенные данные

        Raises:
            ValidationError: Если пользователь уже оставил отзыв на это
                произведение
        """
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.

    Обеспечивает создание и получение комментариев к отзывам.
    Автоматически связывает комментарий с его автором и соответствующим
        отзывом.
    """

    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения объектов модели Title.

    Используется для получения информации о произведениях.
    Включает вложенные данные о категории, жанрах и рейтинге.
    """

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи объектов модели Title.

    Используется при создании и обновлении произведений.
    Позволяет указывать категорию и жанры по их slug-идентификаторам.
    """

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title
