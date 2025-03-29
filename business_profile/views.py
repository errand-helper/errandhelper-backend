from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import BusinessProfile
from .serializers import ProfileSerializer
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError

# Create your views here.
class ProfileRetrieveView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        """Retrieve the BusinessProfile if it exists, else return 404"""
        user = self.request.user
        try:
            return BusinessProfile.objects.get(user=user)
        except BusinessProfile.DoesNotExist:
            raise NotFound({"detail": "Business profile not found."})

    def retrieve(self, request, *args, **kwargs):
        """Custom retrieve method to return profile data if it exists"""
        try:
            profile = self.get_object()
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": "Business profile not found."},status=status.HTTP_404_NOT_FOUND)

class ProfileCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_serializer_context(self):
        return {"request": self.request}
    

class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.business_profile
