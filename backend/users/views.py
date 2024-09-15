import random
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from .serializers import RegisterSerializer, VerifyOtpSerializer
from .serializers import LoginSerializer
from .models import Otp

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Generate OTP
        otp_code = self.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=5)
        Otp.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)
        self.send_otp_email(user.email, otp_code)

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
        from django.core.mail import send_mail
        send_mail(subject, message, 'sohambalekar123@gmail.com', [email])    

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
