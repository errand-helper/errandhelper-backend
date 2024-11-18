from rest_framework import serializers

# from business.serializers import LocationSerializer, SocialMediaSerializer
from profiles.models import Location, Profile, SocialMedia



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["address", "town", "location", "city"]


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ["facebook", "twitter", "linkedin", "instagram", "website"]



class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    user_type = serializers.CharField(source="user.user_type", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)

    bio = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    image = serializers.SerializerMethodField()
    # business_name = serializers.CharField(source="user.business.business_name", read_only=True)
    location = LocationSerializer()
    social_media = SocialMediaSerializer()


    class Meta:
        model = Profile
        fields = ["id", "user_id","first_name", "last_name", "email",
                  "phone_number", "bio", "image", "user_type","location","social_media"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return "https://static.productionready.io/images/smiley-cyrus.jpg"

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        social_media_data = validated_data.pop('social_media', None)

        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        if social_media_data:
            if instance.social_media:
                for attr, value in social_media_data.items():
                    setattr(instance.social_media, attr, value)
                instance.social_media.save()
            else:
                instance.social_media = SocialMedia.objects.create(**social_media_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ProfileImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["image"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return "https://static.productionready.io/images/smiley-cyrus.jpg"

