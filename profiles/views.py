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
        return Profile.objects.get(user=user)

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # def destroy(self, request, *args, **kwargs):
    #     profile = self.get_object()
    #     user = profile.user
    #     # Check and delete related objects if they exist
    #     if profile.location:
    #         profile.location.delete()
    #     if profile.social_media:
    #         profile.social_media.delete()
    #     profile.delete()
    #     user.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProfileImageView(RetrieveAPIView):
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated] 

    def get_object(self):
        return Profile.objects.get(user=self.request.user)