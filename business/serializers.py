from rest_framework import serializers

from authentication.models import User,UserTypes
from authentication.serializers import UserSerializer

from .models import Business


class BusinessRegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    business_name = serializers.CharField()
    registration_number = serializers.CharField()
    activation_fee = serializers.IntegerField()

    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user = UserSerializer(read_only=True)  # Include user details in the response

    class Meta:
        model = Business
        fields = [
            "id","first_name","last_name","email","password","business_name",
            "business_name","registration_number","activation_fee","user"
        ]

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'email': validated_data['email'],
            'password': validated_data['password'],
        }

        user = User.objects.create_user(**user_data)
        user.user_type = UserTypes.BUSINESS

        validated_data.pop('first_name')
        validated_data.pop('last_name')
        validated_data.pop('email')
        validated_data.pop('password')

        business = Business.objects.create(user=user,**validated_data)
        return business
    

