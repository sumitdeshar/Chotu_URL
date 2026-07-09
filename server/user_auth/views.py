from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from user_auth.token import get_tokens_for_user

from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from .services import UserService

COOKIE_NAME = "refresh_token"

def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,   
        samesite="Lax",       
        max_age=7 * 24 * 60 * 60,    
        path="/auth/",              
    )



class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserService.create_user_account(
                email=request.data['email'],
                password=request.data['password'],
                username=request.data.get('username'),
                bio=request.data.get('bio', ''),
            )
        except DjangoValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        tokens = get_tokens_for_user(user)

        response = Response({
            'user': RegisterSerializer(user).data,
            'access': tokens['access'],
        }, status=status.HTTP_201_CREATED)

        set_refresh_cookie(response, tokens['refresh'])
        return response


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = UserService.login_user(
                email=request.data.get('email', ''),
                password=request.data.get('password', ''),
            )
        except DjangoValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        tokens = get_tokens_for_user(user)

        response = Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'access': tokens['access'],
        }, status=status.HTTP_200_OK)

        set_refresh_cookie(response, tokens['refresh'])
        return response
        


from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class TokenRefreshFromCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(COOKIE_NAME)
        if raw_token is None:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(raw_token)
            new_access = str(refresh.access_token)

            response = Response({'access': new_access}, status=status.HTTP_200_OK)

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
                refresh.blacklist()
                user = User.objects.get(id=refresh.payload['user_id'])
                new_refresh = RefreshToken.for_user(user)

                set_refresh_cookie(response, str(new_refresh))

            return response
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User no longer exists.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_token = request.COOKIES.get(COOKIE_NAME)
        response = Response(status=status.HTTP_205_RESET_CONTENT)

        if raw_token:
            try:
                RefreshToken(raw_token).blacklist()
            except TokenError:
                pass

        response.delete_cookie(COOKIE_NAME, path="/auth/")
        return response