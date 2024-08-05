from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,generics

from service.models import Category

# from .models import Category
from .serializers import CategorySerializer
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