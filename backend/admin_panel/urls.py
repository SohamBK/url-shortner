from django.urls import path
from . import views

urlpatterns = [
    path('urls/', views.AdminAllUrlsView.as_view(), name='admin_all_urls'),
    path('analytics/', views.AdminAllAnalyticsView.as_view(), name='admin_all_analytics'),
    path('users/', views.AdminUserListView.as_view(), name='admin-user-list'),
]
