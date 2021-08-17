
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as VE
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from titles.models import Category, Genre, Review, Title

from .filters import TitlesFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrAdminOrModerator
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer)

User = get_user_model()


def create_username(email):
    email = email.lower()
    cleaner = str.maketrans(dict.fromkeys(string.punctuation))
    username = email.translate(cleaner)
    return username


@api_view(['POST'])
def send_generation_code(request):
    email = request.data.get('email')
    try:
        validate_email(email)
    except VE:
        raise ValidationError({'email': 'Enter a valid email address.'})
    email = email.lower()
    cleaner = str.maketrans(dict.fromkeys(string.punctuation))
    username = email.translate(cleaner)
    user, created = User.objects.get_or_create(
        username=username, email=email, is_active=False
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Письмо с кодом подтверждения для доступа на YamDB',
        confirmation_code,
        'admin@yamdb.fake',
        [email],
    )
    return Response({'email': email})


@api_view(['POST'])
def generation_token_for_user(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    if not confirmation_code or not email:
        raise ValidationError(
            {'detail': 'confirmation_code and email are required'}
        )
    user = generics.get_object_or_404(User, email=email)
    context = {'confirmation_code': 'Enter a valid confirmation code'}
    if default_token_generator.check_token(user=user, token=confirmation_code):
        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)
        context = {
            'token': str(refresh.access_token),
        }
    return Response(context)


class UserDetail(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    lookup_field = 'username'
    serializer_class = UserSerializer

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UserMeDetailAPIView(generics.RetrieveUpdateAPIView):
#     queryset = User.objects.all()
#     filter_backends = (filters.SearchFilter,)
#     serializer_class = UserSerializer
#     lookup_field = ['username']
#     search_fields = ['username', ]

#     def get_object(self):
#         instance = get_object_or_404(User, username=self.request.user.username)
#         return instance


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
