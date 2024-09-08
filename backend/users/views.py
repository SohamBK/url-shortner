from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Generate JWT token
        tokens = self.get_tokens_for_user(user)

        return Response({
            'refresh': str(tokens['refresh']),
            'access': str(tokens['access']),
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': refresh,
            'access': refresh.access_token,
        }
