from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import URLAnalytics
from .serializers import URLAnalyticsSerializer

class URLAnalyticsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = URLAnalyticsSerializer

    def get_queryset(self):
        url_id = self.kwargs['url_id']
        return URLAnalytics.objects.filter(url_id=url_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_params = request.query_params
        if 'country' in filter_params:
            queryset = queryset.filter(country=filter_params['country'])
        if 'platform' in filter_params:
            queryset = queryset.filter(platform=filter_params['platform'])
        
        response_data = self.get_serializer(queryset, many=True).data
        return Response({
            'access_count': queryset.count(),
            'analytics_data': response_data
        })
