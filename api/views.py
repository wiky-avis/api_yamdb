import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from titles.models import Category, Genre, Review, Title

from .filters import TitlesFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (
    CategorySerializer, CommentSerializer, ForAdminSerializer,
    ForUserSerializer, GenreSerializer, ReviewSerializer,
    SendConfirmationCodeSerializer, TitleReadSerializer, TitleWriteSerializer,
    СheckingConfirmationCodeSerializer,
)

User = get_user_model()


class SendConfirmationCodeViewSet(generics.CreateAPIView):
    serializer_class = SendConfirmationCodeSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        username = email.split('@')[0]
        confirmation_code = secrets.token_urlsafe(15)
        subject = 'Код подтверждения на Yamdb'
        message = f'Ваш код подтверждения: {confirmation_code}'
        send_mail(
            subject,
            message,
            settings.EMAIL_ADMIN,
            [email],
            fail_silently=False)

        return serializer.save(
            username=username, password=confirmation_code, email=email)


class GetJWTTokenViewSet(TokenObtainPairView):
    serializer_class = СheckingConfirmationCodeSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = ForAdminSerializer
    lookup_field = 'username'
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request, pk=None):
        user = self.request.user
        if request.method == 'PATCH':
            serializer = ForUserSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = ForUserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-id')
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(
            Title.objects.prefetch_related('reviews'),
            id=title_id
        )
        return title

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        author = self.request.user
        title = self.get_title()
        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review.objects.prefetch_related('comments'),
            id=review_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        author = self.request.user
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review.objects.prefetch_related('comments'),
            id=review_id
        )
        serializer.save(
            author=author,
            review=review
        )
