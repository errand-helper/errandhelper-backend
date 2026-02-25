from rest_framework import serializers

from .models import Location, SocialMedia


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["address", "town", "location", "city"]


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ["facebook", "twitter", "linkedin", "instagram", "website"]