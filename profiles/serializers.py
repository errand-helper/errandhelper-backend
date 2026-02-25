from rest_framework import serializers
from authentication.models import User
from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    id_number = serializers.CharField(source="user.id_number", read_only=True)
    created_at = serializers.DateTimeField(source="user.created_at", read_only=True)
    updated_at = serializers.DateTimeField(source="user.updated_at", read_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    image = serializers.SerializerMethodField()
   


    class Meta:
        model = Profile
        fields = ["id", "user_id","first_name", "last_name", "email",
                  "phone_number", "bio", "image", "role","id_number","created_at","updated_at"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return "https://static.productionready.io/images/smiley-cyrus.jpg"

    def update(self, instance, validated_data):
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




