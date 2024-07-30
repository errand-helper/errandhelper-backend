from rest_framework import serializers

from profiles.models import Profile



class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(source="user.first_name",read_only=True)
    last_name = serializers.CharField(source="user.last_name",read_only=True)
    email = serializers.EmailField(source="user.email",read_only=True)
    user_type = serializers.EmailField(source="user.user_type",read_only=True)

    bio = serializers.CharField(required=False,allow_blank=True)
    city = serializers.CharField(required=False,allow_blank=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("id", "first_name", "last_name", "email", "bio", "city", "image", "user_type")



    def get_image(self,obj):
        if obj.image:
            return obj.image.url
        return "https://static.productionready.io/images/smiley-cyrus.jpg"
