from rest_framework import serializers
from .models import shortnedURL
import random, string

class ShortnedUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = shortnedURL
        fields = ['original_url', 'expires_at']

    def create(self, validated_data):
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        while shortnedURL.objects.filter(short_code=short_code).exists():
            short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        user = self.context['request'].user
        return shortnedURL.objects.create(user=user, short_code=short_code, **validated_data)

