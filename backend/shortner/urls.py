from django.urls import path
from .views import CreateShortUrlView, RedirectUrlView, UserShortnedUrlListView

urlpatterns = [
    path('shorten/', CreateShortUrlView.as_view(), name='create-short-url'),
    path('user/urls/', UserShortnedUrlListView.as_view(), name='user_urls'),
]