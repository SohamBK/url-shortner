from django.shortcuts import render
from rest_framework import generics 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.conf import settings
from .models import shortnedURL
from .serializers import ShortnedUrlSerializer

class CreateShortUrlView(APIView):
    serializer_class = ShortnedUrlSerializer
    permission_classes = [permission.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        short_url_instance = serializer.save()

        # Construct the shortened URL
        short_url = f"{settings.BASE_URL}/{short_url_instance.short_code}"
        
        return Response({
            'short_url': short_url,
            'expires_at': short_url_instance.expires_at,
            'is_active': short_url_instance.is_active
        })