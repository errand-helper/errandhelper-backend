from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status,generics

from business.models import Business

# from .models import Category
from .serializers import BusinessRegisterSerializer, BusinessRetrieve

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
    

class BusinessDetailView(APIView):
    def get(self, request, user_id):
        # Filter business by the given user ID
        try:
            business = Business.objects.get(user_id=user_id)
            # Serialize the business data
            serializer = BusinessRetrieve(business)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            # If no business is found for the given user ID
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
    # def get(self, request, business_id):
    #     try:
    #         # Get the business instance by its ID
    #         business = Business.objects.get(id=business_id)
            
    #         # Serialize the business data
    #         serializer = BusinessRetrieve(business)
            
    #         # Return the serialized data
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Business.DoesNotExist:
    #         # Return a 404 response if the business does not exist
    #         return Response({"error": "Business not found."}, status=status.HTTP_404_NOT_FOUND)
    
class ListBusinesses(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def get(self,request,format=None):
        businesses = Business.objects.all()
        serializer = BusinessRegisterSerializer(businesses,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

