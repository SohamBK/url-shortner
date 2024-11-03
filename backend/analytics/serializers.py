from rest_framework import serializers
from .models import URLAnalytics

class URLAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLAnalytics
        fields = [
            'timestamp', 'ip_address', 'user_agent', 'referrer',
            'country', 'platform', 'device_type', 'access_count'
        ]
