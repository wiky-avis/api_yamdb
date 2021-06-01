import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (SendCodeSerializer, UserSerializer,
                          СheckingConfirmationCodeSerializer)

User = get_user_model()


class SendCodeViewSet(generics.CreateAPIView):
    serializer_class = SendCodeSerializer
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
    serializer_class = UserSerializer
    queryset = User.objects.all()
