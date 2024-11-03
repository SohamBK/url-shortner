from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from shortner.models import shortnedURL
from analytics.models import URLAnalytics
from users.models import User
from users.serializers import UserSerializer
from .serializers import ShortnedUrlAdminSerializer
from .serializers import URLAnalyticsAdminSerializer

class AdminAllUrlsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        filter_params = request.query_params
        queryset = shortnedURL.objects.all()

        # Apply filters if provided
        if 'is_active' in filter_params:
            queryset = queryset.filter(is_active=filter_params['is_active'])
        if 'is_expired' in filter_params:
            queryset = queryset.filter(expires_at__lt=timezone.now())

        serializer = ShortnedUrlAdminSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAllAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        filter_params = request.query_params
        queryset = URLAnalytics.objects.all()

        if 'country' in filter_params:
            queryset = queryset.filter(country=filter_params['country'])

        serializer = URLAnalyticsAdminSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        is_active = request.query_params.get('is_active')
        
        # Filter users based on the `is_active` parameter, if provided
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            users = User.objects.filter(is_active=is_active)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)