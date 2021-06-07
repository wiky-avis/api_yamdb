from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, GetJWTTokenViewSet,
    ReviewViewSet, SendConfirmationCodeViewSet, TitleViewSet, UserViewSet,
)

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='Review')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='Comment')
v1_router.register(
    'titles',
    TitleViewSet,
    basename='title',
)
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='category',
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genre',
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path(
        'v1/auth/email/',
        SendConfirmationCodeViewSet.as_view(),
        name='send_confirmation_code'),
    path('v1/auth/token/', GetJWTTokenViewSet.as_view(), name='get_jwt_token'),
]
