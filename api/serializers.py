from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')
        model = User


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
