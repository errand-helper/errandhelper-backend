from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status,generics

from business.models import Business

# from .models import Category
from .serializers import BusinessRegisterSerializer

# Create your views here.


class RegisterBusiness(APIView):
    permission_classes = [AllowAny]
    serializer_class = BusinessRegisterSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ListBusinesses(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def get(self,request,format=None):
        businesses = Business.objects.all()
        serializer = BusinessRegisterSerializer(businesses,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

