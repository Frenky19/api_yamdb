from rest_framework.viewsets import ModelViewSet

from reviews.models import Category, Genre, Title
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)
from users.permissions import IsAdmin
#from api.filters import TitleFilter


class CategoryViewSet(ModelViewSet):
    """Представление для управления категориями."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    lookup_field = 'slug'
    #filter_backends = [filters.SearchFilter]
    #search_fields = ['name'] #чуть позже допишу файл фильтр 

    def perform_create(self, serializer):
        serializer.save()


class GenreViewSet(ModelViewSet):
    """Представление для управления жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'slug'
    #filter_backends = [filters.SearchFilter]
    #search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save()


class TitleViewSet(ModelViewSet):
    """Представление для управления произведениями."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdmin]
    #filter_backends = [DjangoFilterBackend]
    #filterset_class = TitleFilter

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()  
