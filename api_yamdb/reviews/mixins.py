from django.db.models import Avg


class UpdateRatingMixin:
    """
    Миксин для обновления среднего рейтинга произведения.
    """
    def update_title_rating(self, title):
        """
        Обновляет средний рейтинг произведения на основе всех отзывов.

        :param title: Произведение, для которого нужно обновить рейтинг.
        """
        reviews = title.reviews.all()
        title.rating = (
            reviews.aggregate(Avg('score'))['score__avg']
            if reviews.exists() else None
        )
        title.save()
