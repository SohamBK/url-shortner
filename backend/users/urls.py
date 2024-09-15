from django.urls import path
from users.views import RegisterView, LoginView, VerifyOtpview, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOtpview.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uuid:uid>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]