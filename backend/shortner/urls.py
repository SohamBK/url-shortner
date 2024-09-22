from django.urls import path
from users.views import RegisterView, LoginView, VerifyOtpview, ForgotPasswordView, ResetPasswordView
from .views import CreateShortUrlView

urlpatterns = [
    path('shorten/', CreateShortUrlView.as_view(), name='create-short-url'),
]