from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from rest_framework import generics 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.conf import settings
from .models import shortnedURL
from .serializers import ShortnedUrlSerializer
import requests

class CreateShortUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ShortnedUrlSerializer(data=request.data,  context={'request': request})
        serializer.is_valid(raise_exception=True)
        short_url_instance = serializer.save()

        # Construct the shortened URL
        short_url = f"{settings.BASE_URL}/{short_url_instance.short_code}"
        
        return Response({
            'short_url': short_url,
            'expires_at': short_url_instance.expires_at,
            'is_active': short_url_instance.is_active
        })
    
class RedirectUrlView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_code, *args, **kwargs):
        url_instance = get_object_or_404(shortnedURL, short_code = short_code, is_active=True)

        if url_instance.is_expired():
            return Response({
                'error' : 'The shortned url is expired'
            }, status=status.HTTP_410_GONE)

        client_ip = self.get_client_ip(request)
        self.log_analytics(url_instance, client_ip, request)
        
        return redirect(url_instance.original_url)
    
    def get_client_ip(self, request):
        """Helper to get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_analytics(self, url_instance, client_ip, request):
        """Fetch location info and log analytics data"""
        try:
            location_info = self.get_location_info(client_ip)
            url_instance.analytics.create(
                ip_address=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', ''),
                country=location_info.get('country', 'Unknown')
            )
        except Exception as e:
            # Log the error to a logging system, but don't disrupt the redirect
            print(f"Error logging analytics: {e}")

    def get_location_info(self, ip):
        """Fetch location info from ipinfo.io"""
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
