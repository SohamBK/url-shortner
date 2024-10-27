from rest_framework.views import APIView
from django.db.models import Count, F, Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import TruncMonth, TruncWeek

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
    
class AnalyticsAggregationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        url_id = self.kwargs['url_id']
        period = request.query_params.get('period', 'monthly')

        # Choose truncation method based on requested period
        if period == 'weekly':
            trunc_period = TruncWeek('timestamp')
        else:
            trunc_period = TruncMonth('timestamp')

        # Aggregate data by period
        analytics_data = (
            URLAnalytics.objects
            .filter(url_id=url_id)
            .annotate(period=trunc_period)
            .values('period')
            .annotate(
                total_visits=Count('id'),  # Count total visits
                unique_visitors=Count('ip_address', distinct=True),  # Count unique visitors
                top_referrer=F('referrer')  # Get the top referrer
            )
            .order_by('-period')  # Order by period, descending
        )

        # Prepare response data
        response_data = []
        for data in analytics_data:
            # Query top referrers for each period
            top_referrers = (
                URLAnalytics.objects
                .filter(url_id=url_id, timestamp__year=data['period'].year, timestamp__month=data['period'].month)
                .values('referrer')
                .annotate(ref_count=Count('referrer'))
                .order_by('-ref_count')[:5]
            )

            response_data.append({
                'period': data['period'],
                'total_visits': data['total_visits'],
                'unique_visitors': data['unique_visitors'],
                'top_referrers': list(top_referrers),
            })

        return Response(response_data)