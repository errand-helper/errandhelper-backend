from rest_framework import serializers

from authentication.models import User,UserTypes
from authentication.serializers import UserSerializer
from profiles.models import Location, SocialMedia
from service.models import Category
from service.serializers import CategorySerializer

from .models import Business, BusinessCategory








class BusinessRegisterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    business_name = serializers.CharField()
    registration_number = serializers.CharField()
    # activation_fee = serializers.IntegerField()

    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    user = UserSerializer(read_only=True)  # Include user details in the response
   

    class Meta:
        model = Business
        fields = [
            "id","first_name","last_name","email","password",'confirm_password',"business_name", "business_name","registration_number","user"
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password":"Passwords do not match"})
        return super().validate(attrs)
    
    def create(self, validated_data):
        # Extract user-related data
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
        }
        validated_data.pop('confirm_password')  # Remove confirm_password, not needed for creating a user

        # Create the User instance
        user = User.objects.create_user(**user_data)
        user.set_password(user_data['password'])
        user.user_type = UserTypes.BUSINESS
        user.save()

        # Create Location instance
        location_data = validated_data.pop('location')
        location = Location.objects.create(**location_data)

        # Create SocialMedia instance
        social_media_data = validated_data.pop('social_media')
        social_media = SocialMedia.objects.create(**social_media_data)

        # Create the Business instance with the created user, location, and social media
        business = Business.objects.create(
            user=user,
            location=location,
            social_media=social_media,
            **validated_data
        )

        return business


    # def create(self, validated_data):
    #     user_data = {
    #         'first_name': validated_data['first_name'],
    #         'last_name': validated_data['last_name'],
    #         'email': validated_data['email'],
    #         'password': validated_data['password'],
    #     }

    #     user = User.objects.create_user(**user_data)
    #     user.set_password(validated_data['password'])

    #     user.user_type = UserTypes.BUSINESS
    #     user.save()


    #     validated_data.pop('first_name')
    #     validated_data.pop('last_name')
    #     validated_data.pop('email')
    #     validated_data.pop('password')
    #     validated_data.pop('confirm_password')


    #     business = Business.objects.create(user=user,**validated_data)
    #     return business
    
class BusinessRetrieve(serializers.ModelSerializer):

     class Meta:
        model = Business
        fields = '__all__'


class BusinessCategorySerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, many=True
    )

    class Meta:
        model = BusinessCategory
        fields = ['id', 'business', 'categories', 'category_ids']

    def create(self, validated_data):
        # Extract category IDs and business from validated_data
        category_ids = validated_data.pop('category_ids')
        business = validated_data.pop('business')

        # Create the BusinessCategory instance
        business_category = BusinessCategory.objects.create(business=business, **validated_data)

        # Set the categories for the BusinessCategory instance
        business_category.categories.set(category_ids)

        return business_category
    
    def update(self, instance, validated_data):
        # Get new category IDs from validated_data
        category_ids = validated_data.pop('category_ids', None)

        # Update business field if present
        instance.business = validated_data.get('business', instance.business)

        # If category IDs are provided, update the related categories
        if category_ids is not None:
            instance.categories.set(category_ids)

        # Save the updated instance
        instance.save()
        return instance
    
    
