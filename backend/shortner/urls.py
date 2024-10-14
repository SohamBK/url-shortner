from django.urls import path
from .views import CreateShortUrlView, RedirectUrlView, UserShortnedUrlListView, ShortnedUrlUpdateView, ShortnedUrlDeleteView

urlpatterns = [
    path('shorten/', CreateShortUrlView.as_view(), name='create-short-url'),
    path('user/urls/', UserShortnedUrlListView.as_view(), name='user_urls'),
    path('urls/<int:pk>/update/', ShortnedUrlUpdateView.as_view(), name='shortened-url-update'),
    path('urls/<int:pk>/delete/', ShortnedUrlDeleteView.as_view(), name='shortened-url-delete'),
]