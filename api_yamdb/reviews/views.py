from rest_framework import viewsets

from reviews.mixins import UpdateRatingMixin
from reviews.models import Review, Comment
from api.serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(UpdateRatingMixin, viewsets.ModelViewSet):
    """Представление для управления отзывами."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        """Создание отзыва и обновление рейтинга произведения."""
        review = serializer.save(user=self.request.user)
        self.update_title_rating(review.title)

    def perform_update(self, serializer):
        """Обновление отзыва и рейтинга произведения."""
        review = serializer.save()
        self.update_title_rating(review.title)

    def perform_destroy(self, instance):
        """
        Удаление отзыва и обновление рейтинга произведения.
        """
        title = instance.title
        instance.delete()
        self.update_title_rating(title)


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для управления комментариями к отзывам."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
