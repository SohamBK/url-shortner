import random
import logging
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from datetime import timedelta
from django.utils import timezone
from .serializers import RegisterSerializer, VerifyOtpSerializer, PasswordResetSerializer, ResetPasswordSerializer
from .serializers import LoginSerializer
from .models import Otp

User = get_user_model()
logger = logging.getLogger('url_shortner')

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Generate OTP
        expires_at = timezone.now() + timedelta(minutes=5)
        Otp.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)
        try:
            self.send_otp_email(user.email, otp_code)
        except (EmailMessage.Error, smtplib.SMTPException) as e:
            # Handle email sending error gracefully
            logger.error(f'An error occurred: {e}')
            return Response({
                'message': 'An error occurred while sending the OTP. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message' : 'Otp sent to your email. Please verify to complete registration process',
        }, status = status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()
    
    def generate_otp(self):
        return str(random.randint(100000,999999))

    def send_otp_email(self, email, otp_code):
        subject = "URL Shrotner Verification Code"
        message = f"Your OTP code is {otp_code}. It is valid for 5 minutes."
        email = EmailMessage(subject=subject, body=message, from_email=settings.EMAIL_HOST_USER, to=[email])
        email.send(fail_silently=False)
            

class VerifyOtpview(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        otp_code = serializer.validated_data['otp_code']

        try:
            otp_entry = Otp.objects.get(user=user, otp_code=otp_code)
        except Otp.DoesNotExist:
            return Response({
                'detail' : 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp_entry.is_valid():
            return Response({'detail': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.save()

        otp_entry.delete()

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'OTP verified successfully. Your account is now active.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
    
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to access

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(email=email, password=password)

            if user is not None:
                # If the user is authenticated, generate the JWT tokens
                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse('reset-password', args=[user.pk, token])
                )

                # send email
                try:
                    send_mail(
                        'Reset Password',
                        f'Click the link to reset your password: {reset_url}',
                        'from@example.com',
                        [email],
                        fail_silently=False
                    )

                    return Response({
                        'message' : 'Password reset link sent to your registered mail.'
                    }, status=status.HTTP_200_OK)
                
                except Exception as e:
                    logger.error(f'Error while sending password reset link: {e}')
                    return Response({
                        'error' : 'There wan error while sending password reset link to your email. Please try again later.'
                    }, status=status.HTTP_500_BAD_REQUEST)
                
            return Response({
                'error' : 'Email not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uid, token, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Since uid is a UUID, directly query using pk=uid
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the token is valid
            if not default_token_generator.check_token(user, token):
                return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

            # Save the new password
            serializer.save(uid, token)
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)