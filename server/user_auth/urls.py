from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView, TokenRefreshFromCookieView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
     path('token/refresh/', TokenRefreshFromCookieView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]