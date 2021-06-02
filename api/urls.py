from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (GetJWTTokenViewSet, ReviewViewSet,
                    SendConfirmationCodeViewSet, UserViewSet)

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
# v1_router.register('reviews', ReviewViewSet, basename='Review')
v1_router.register(
    r'titles/(?P<id>\d+)/reviews', ReviewViewSet, basename='Review')


urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path(
        'v1/auth/email/',
        SendConfirmationCodeViewSet.as_view(),
        name='send_confirmation_code'),
    path('v1/auth/token/', GetJWTTokenViewSet.as_view(), name='get_jwt_token'),
]
