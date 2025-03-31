from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CategoryViewSet, TitleViewSet
from reviews.views import ReviewViewSet
from users.views import UserViewSet

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserViewSet, basename='users')
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('auth/', include('users.urls')),
]
