
from rest_framework import serializers

from media_location.models import Location, SocialMedia

from .models import BusinessProfile
from media_location.serializers import LocationSerializer, SocialMediaSerializer



class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    user_type = serializers.CharField(source="user.user_type", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    business_id = serializers.CharField(source="business.id", read_only=True)

    bio = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    image = serializers.SerializerMethodField()
    
    location = LocationSerializer(required=False)  # Nested Serializer
    social_media = SocialMediaSerializer(required=False)  # Nested Serializer

    class Meta:
        model = BusinessProfile
        fields = ["id", "user_id", "email","phone_number", "bio", "image", "user_type", "location", "social_media","business_id"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return "https://static.productionready.io/images/smiley-cyrus.jpg"
    
    def create(self, validated_data):
        user = self.context["request"].user

        # Extract nested data
        location_data = validated_data.pop("location", None)
        social_media_data = validated_data.pop("social_media", None)

        # Create or assign location
        location = None
        if location_data:
            location, _ = Location.objects.get_or_create(**location_data)

        # Create or assign social media
        social_media = None
        if social_media_data:
            social_media, _ = SocialMedia.objects.get_or_create(**social_media_data)

        # Get a single Business instance associated with the user.
        # Adjust this based on how your models are related.
        business = user.business.first()  # Ensure this returns a Business instance.

        # Create the business profile
        business_profile = BusinessProfile.objects.create(
            user=user,
            business=business,
            location=location,
            social_media=social_media,
            **validated_data
        )

        return business_profile


    # def create(self, validated_data):
    #     user = self.context["request"].user
    #     business = self.context["request"].business

    #     # Extract nested data
    #     location_data = validated_data.pop("location", None)
    #     social_media_data = validated_data.pop("social_media", None)

    #     # Create or assign location
    #     location = None
    #     if location_data:
    #         location, _ = Location.objects.get_or_create(**location_data)

    #     # Create or assign social media
    #     social_media = None
    #     if social_media_data:
    #         social_media, _ = SocialMedia.objects.get_or_create(**social_media_data)

    #     # Create the business profile
    #     business_profile = BusinessProfile.objects.create(
    #         user=user,
    #         business=business,
    #         location=location,
    #         social_media=social_media,
    #         **validated_data
    #     )

    #     return business_profile
    

    def update(self, instance, validated_data):
        # Handle nested fields
        location_data = validated_data.pop("location", None)
        social_media_data = validated_data.pop("social_media", None)

        # Update location if provided
        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        # Update social media if provided
        if social_media_data:
            if instance.social_media:
                for attr, value in social_media_data.items():
                    setattr(instance.social_media, attr, value)
                instance.social_media.save()
            else:
                instance.social_media = SocialMedia.objects.create(**social_media_data)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    


class BusinessProfileMinimalSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.business_name",read_only=True)
    business_id = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    is_approved =  serializers.CharField(read_only=True)
    image =  serializers.CharField(read_only=True)
    location = LocationSerializer()
    email = serializers.EmailField(source="user.email",read_only=True)
    user_id = serializers.CharField(source="user.id",read_only=True)

    class Meta:
        model = BusinessProfile
        fields = ["business_id", "bio","business_name","phone_number","is_approved","image","location","email","user_id"]

    # def get_business_id(self, obj):
    #     return obj.business_id




# class ProfileSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     email = serializers.EmailField(source="user.email", read_only=True)
#     user_type = serializers.CharField(source="user.user_type", read_only=True)
#     user_id = serializers.CharField(source="user.id", read_only=True)

#     bio = serializers.CharField(required=False, allow_blank=True)
#     phone_number = serializers.CharField(required=False, allow_blank=True)
#     image = serializers.SerializerMethodField()
#     location = LocationSerializer()
#     social_media = SocialMediaSerializer()


#     class Meta:
#         model = BusinessProfile
#         fields = ["id", "user_id", "email",
#                   "phone_number", "bio", "image", "user_type","location","social_media"]

#     def get_image(self, obj):
#         if obj.image:
#             return obj.image.url
#         return "https://static.productionready.io/images/smiley-cyrus.jpg"

