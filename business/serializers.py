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
    confirm_password = serializers.CharField(write_only=True)

    user = UserSerializer(read_only=True)  # Include user details in the response

    class Meta:
        model = Business
        fields = [
            "id","first_name","last_name","email","password",'confirm_password',"business_name", "business_name","registration_number","activation_fee","user"
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password":"Passwords do not match"})
        return super().validate(attrs)

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'email': validated_data['email'],
            'password': validated_data['password'],
        }

        user = User.objects.create_user(**user_data)
        user.set_password(validated_data['password'])

        user.user_type = UserTypes.BUSINESS
        user.save()


        validated_data.pop('first_name')
        validated_data.pop('last_name')
        validated_data.pop('email')
        validated_data.pop('password')
        validated_data.pop('confirm_password')


        business = Business.objects.create(user=user,**validated_data)
        return business
    
class BusinessRetrieve(serializers.ModelSerializer):

     class Meta:
        model = Business
        fields = '__all__'

