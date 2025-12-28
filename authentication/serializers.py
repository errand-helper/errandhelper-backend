# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
# from .models import ClientProfile
from django.db import transaction

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id","role"]

        


# class ClientProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClientProfile
#         exclude = ['user']


# BusinessProfileSerializer removed - business profiles now handled in business app



# from rest_framework import serializers
# from django.contrib.auth.password_validation import validate_password

# from authentication.models import User, UserTypes
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken



# class RegistrationSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True, format='hex')
#     password = serializers.CharField(max_length=128,min_length=8,write_only=True, validators=[validate_password])
#     confirm_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['id','first_name','last_name','id_number','email','password','confirm_password']


#     def validate(self,attrs):
#         if attrs['password'] != attrs['confirm_password']:
#             raise serializers.ValidationError({"password":"Passwords do not match"})
#         return attrs
    
#     def create(self,validated_data):
#         validated_data.pop('confirm_password')
#         self.user_type = UserTypes.CUSTOMER
#         user = User.objects.create_user(**validated_data)

#         # print(user)

#         user.set_password(validated_data['password'])
#         user.save()
#         return user


# class LoginSerializer(serializers.Serializer):
#     id = serializers.UUIDField(read_only=True, format='hex')
#     email = serializers.EmailField()
#     password = serializers.CharField(max_length=128, write_only=True)
#     # token = serializers.CharField(max_length=255, read_only=True)
#     user_type = serializers.CharField(max_length=255, read_only=True)

#     class Meta:
#         model = User
#         fields = ["id", 'email',"user_type"]

#     def validate(self, data):
#         email = data.get('email', None)
#         password = data.get('password', None)

#         if email is None:
#             raise serializers.ValidationError("Email is required to log in.")
#         if password is None:
#             raise serializers.ValidationError("Password is required to log in.")

#         user = authenticate(email=email, password=password)

#         if not user:
#             raise serializers.ValidationError("A user with this email and password was not found.")
        
#         if not user.is_active:
#             raise serializers.ValidationError("This user has been deactivated.")

#         refresh = RefreshToken.for_user(user)
#         return {
#             'id': user.id,
#             'email': user.email,
#             'user_type':user.user_type,
#             'refresh': str(refresh),
#             'access': str(refresh.access_token), # type: ignore
#         }
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'email']



# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True, validators=[validate_password])