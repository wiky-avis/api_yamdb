from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from titles.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')
        read_only_fields = ('role', 'email')


class ForAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')


class SendConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'detail': 'Пользователь с таким email уже есть в нашей базе'})
        return email

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class СheckingConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(
            User,
            email=email,
            password=confirmation_code,
            is_active=True)
        if user is None:
            raise serializers.ValidationError(
                {
                    'detail': 'Такого пользователя нет или неверный код '
                    'подтверждения или email'})
        token = {'token': str(AccessToken.for_user(user))}
        return token


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return CategorySerializer(value).data


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return GenreSerializer(value).data


class TitleSerializer(serializers.ModelSerializer):
    category = CategoryField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )
    genre = GenreField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('__all__')
        read_only_fields = ('title_id',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('__all__')
        model = Comment
        read_only_fields = ('review_id',)
