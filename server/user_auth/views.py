from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.views import APIView

from .services import UserService
from .serializers import *

# Create your views here.
def home(request):
    context = {
        "start": "world"
    }
    
    return JsonResponse(context)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        print(serializer)
        
        # if serializer.is_valid():
        #     user = UserService.create_user_account(**serializer.validated_data)
            
        #     return Response({"message": "Success"}, status=201)
        return serializer


