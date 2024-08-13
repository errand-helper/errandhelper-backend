from django.http import Http404
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status,generics

from service.models import Category, Service
from service.permissions import IsOwnerOfBusinessProfile

# from .models import Category
from .serializers import CategorySerializer, ServiceSerializer
# Create your views here.
class CategoryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated] # only admin to add category but everyone can view
    serializer_class = CategorySerializer

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() and request.user.is_staff:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif not request.user.is_staff: # remove here permission to add service category"
            return Response({"error": "You don't have permission to add service category"}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = self.serializer_class(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ServiceView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerOfBusinessProfile] # add is
    serializer_class = ServiceSerializer

    def get(self,request,format=None):
        services = Service.objects.all()
        serializer = self.serializer_class(services,many=True)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def post(self,request,format=None):
        serializer = self.serializer_class(data=request.data)
        print(request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class ServiceDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ServiceSerializer
    def get_object(self,pk):
        try:
            return Service.objects.get(pk=pk)
        except Service.DoesNotExist:
            return Http404
        
    def put(self,request,pk,format=None):
        service = self.get_object(pk)
        serializer = self.serializer_class(service,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
