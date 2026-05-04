from rest_framework import serializers
from shortner.models import shortnedURL
from analytics.models import URLAnalytics

class ShortnedUrlAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = shortnedURL
        fields = ['id', 'original_url', 'short_code', 'is_active', 'expires_at', 'created_at', 'updated_at', 'user']

class URLAnalyticsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLAnalytics
        fields = ['id', 'url', 'timestamp', 'ip_address', 'user_agent', 'referrer', 'country', 'platform']
