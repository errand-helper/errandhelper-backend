from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView,RetrieveUpdateDestroyAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from profiles.models import Profile
from profiles.serializers import ProfileImageSerializer, ProfileSerializer

# Create your views here.
class ProfileRetrieveView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        return Profile.objects.get(user=user) # type: ignore

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        allowed_fields = {'phone_number', 'bio'}
        filtered_data = {field: value for field, value in request.data.items() if field in allowed_fields}
        serializer = self.serializer_class(profile, data=filtered_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ProfileImageView(RetrieveAPIView):
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated] 

    def get_object(self):
        return Profile.objects.get(user=self.request.user) # type: ignore