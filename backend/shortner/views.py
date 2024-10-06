import logging
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from django.db.models import Count
from rest_framework import generics 
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, get_object_or_404

from .models import shortnedURL, URLAnalytics
from .serializers import ShortnedUrlSerializer
from .services.cache_service import UrlCacheService

logger = logging.getLogger('url_shortner')

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
        # Try to fetch the URL data from Redis cache
        cached_data = UrlCacheService.get_cached_url(short_code)
        
        if cached_data:
            original_url = cached_data.get('original_url')
            url_id = cached_data.get('url_id')
            client_ip = self.get_client_ip(request)
            self.log_analytics(url_id, client_ip, request)
            
            return redirect(original_url)
        
        url_instance = get_object_or_404(shortnedURL, short_code=short_code, is_active=True)

        # Check if the URL is expired
        if url_instance.is_expired():
            return Response({
                'error': 'The shortened URL is expired'
            }, status=status.HTTP_410_GONE)
        
        # Cache the URL data for future requests
        UrlCacheService.cache_url_data(short_code, {
            'original_url': url_instance.original_url,
            'url_id': url_instance.id,
            'expires_at': url_instance.expires_at.isoformat() if url_instance.expires_at else None,
        }, expiry_date=url_instance.expires_at)
        
        # Log analytics
        client_ip = self.get_client_ip(request)
        self.log_analytics(url_instance.id, client_ip, request)
        
        return redirect(url_instance.original_url)
    
    def get_client_ip(self, request):
        """
            Helper to get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_analytics(self, url_id, client_ip, request):
        """
            Fetch location info and log analytics data
        """
        try:
            location_info = self.get_location_info(client_ip)
            URLAnalytics.objects.create(
                url_id=url_id,
                ip_address=client_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER', ''),
                country=location_info.get('country', 'Unknown')
            )
        except Exception as e:
            logger.error(f'Error logging analytics: {e}')


    def get_location_info(self, ip):
        """
            Fetch location info from ipinfo.io
        """
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
        
class UserShortnedUrlListView(APIView):
    """
    List all urls created by a user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        urls = shortnedURL.objects.filter(user=user)

        if urls is None:
            return Response([], status=status.HTTP_200_OK)
        
        is_active=request.query_params.get('is_active') # True or False
        is_expired=request.query_params.get('is_expired') # True or False
        sort_by=request.query_params.get('sort_by') #most_used, created_at

        if is_active is not None:
            urls = urls.filter(is_active=is_active.lower == 'true')

        if is_expired is not None:
            if is_expired.lower == 'true':
                urls = urls.filter(expires_at__lt=timezone.now())
            else:
                urls = urls.filter(expires_at__gte=timezone.now())

        if sort_by == 'created_at':
            urls = urls.order_by('-created_at')
        elif sort_by == 'most_used':
            urls = urls.annotate(num_hits=Count('analytics')).order_by('-num_hits')

        # Serialize the results
        serializer = ShortnedUrlSerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)