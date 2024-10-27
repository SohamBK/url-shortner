from django.urls import path
from .views import URLAnalyticsView, AnalyticsAggregationView

urlpatterns = [
    path('analytic-info/<int:url_id>/', URLAnalyticsView.as_view(), name='url-analytics'),
    path('aggregation/<int:url_id>/', AnalyticsAggregationView.as_view(), name='url-analytics-aggregation'),
]
