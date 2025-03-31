from django.contrib import admin

from .models import Review, Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Review.
    """
    list_display = ('id', 'title', 'user', 'score', 'pub_date')
    search_fields = ('title__name', 'user__username', 'text')
    list_filter = ('score', 'pub_date')
    raw_id_fields = ('title', 'user')
    ordering = ('-pub_date',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Comment.
    """
    list_display = ('id', 'review', 'user', 'text', 'pub_date')
    search_fields = ('review__title__name', 'user__username', 'text')
    list_filter = ('pub_date',)
    raw_id_fields = ('review', 'user')
    ordering = ('-pub_date',)
