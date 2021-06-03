import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
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
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SendConfirmationCodeSerializer, TitleSerializer,
                          UserSerializer, СheckingConfirmationCodeSerializer)

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
        from_email = 'admin@yamdb.ru'
        send_mail(subject, message, from_email, [email], fail_silently=False)

        return serializer.save(
            username=username, password=confirmation_code, email=email)


class GetJWTTokenViewSet(TokenObtainPairView):
    serializer_class = СheckingConfirmationCodeSerializer


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request, pk=None):
        user = get_object_or_404(User, email=self.request.user.email)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(self.request.user)
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
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrAdminOrModerator]

    def get_queryset(self):
        title_id = self.kwargs.get('id')
        title = get_object_or_404(
            Title.objects.prefetch_related('reviews'),
            id=title_id
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        author = self.request.user
        title_id = self.kwargs.get('id')
        title = get_object_or_404(
            Title.objects.prefetch_related('reviews'),
            id=title_id
        )
        serializer.save(
            author=author,
            title_id=title
        )


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
            review_id=review
        )
