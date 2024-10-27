from django.urls import path
from .views import URLAnalyticsView

urlpatterns = [
    path('analytic-info/<int:url_id>/', URLAnalyticsView.as_view(), name='url-analytics'),
]
