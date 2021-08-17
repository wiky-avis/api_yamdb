from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserDetail,
                    generation_token_for_user, send_generation_code)

v1_router = DefaultRouter()
v1_router.register('users', UserDetail)
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
    #path('v1/users/me/', UserMeDetailAPIView.as_view(), name='me_detail'),
    path(
        'v1/auth/email/', send_generation_code, name='generation_token_for_user'),
    path('v1/auth/token/', generation_token_for_user, name='send_generation_code'),
]
