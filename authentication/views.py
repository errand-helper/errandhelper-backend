# accounts/views.py
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import ClientProfile
from .serializers import (
    UserSignupSerializer,
    ClientProfileSerializer
)
# accounts/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token
        token['role'] = user.role
        # token['email'] = user.email
        # token['id'] = str(user.id) 
        # token['first_name'] = user.first_name
        # token['last_name'] = user.last_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user information to the response
        data['id'] = str(self.user.id)
        # data['email'] = self.user.email
        data['role'] = self.user.role
        # data['first_name'] = self.user.first_name
        # data['last_name'] = self.user.last_name
        return data

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from rest_framework import status
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    # 'success': True,
                    'message': 'User created successfully.',
                    # 'user': {
                    #     'id': str(user.id),
                    #     'email': user.email,
                    #     'role': user.role,
                    #     'first_name': user.first_name,
                    #     'last_name': user.last_name
                    # }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    # 'success': False,
                    'message': 'Failed to create user.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                # 'success': False,
                'message': f'An error occurred: {str(e)}',
                'errors': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = ClientProfile.objects.get_or_create(user=self.request.user)
        return profile


# BusinessProfileView removed - business profiles now handled in business app




















# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny, IsAuthenticated

# from authentication.serializers import ChangePasswordSerializer, LoginSerializer, RegistrationSerializer
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authentication import TokenAuthentication

    

# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = RegistrationSerializer
#     # authentication_classes = []

#     def post(self, request):
#         # user = request.data.get("user", {})
#         user_data = request.data
#         serializer = self.serializer_class(data=user_data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         # serializer.save()
#         # refresh = RefreshToken.for_user(user)
#         # # print(refresh)
#         # tokens = {
#         #     'refresh':str(refresh),
#         #     'access':str(refresh.access_token)
#         # } {'user':serializer.data},
#         return Response("Created successfully",status=status.HTTP_201_CREATED)
    
    
# class LoginView(APIView):
#     permission_classes = (AllowAny,)
#     serializer_class = LoginSerializer
#     authentication_classes = []

#     def post(self, request):
#         user_data = request.data
#         serializer = self.serializer_class(data=user_data)
#         serializer.is_valid(raise_exception=True)

#         # Get the validated data, which includes the tokens
#         validated_data = serializer.validated_data

#         # print(validated_data)

#         return Response(
#             {
#                 # 'user': {
#                     'id': validated_data['id'], # type: ignore
#                     'email': validated_data['email'], # type: ignore
#                     'user_type': validated_data['user_type'], # type: ignore
#                     'access': validated_data['access'], # type: ignore
#                     'refresh': validated_data['refresh'], # type: ignore


#                 # },
#             }, # type: ignore
#             status=status.HTTP_200_OK
#         )


# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = ChangePasswordSerializer(data=request.data)
#         user = request.user

#         if serializer.is_valid():
#             old_password = serializer.validated_data['old_password'] # type: ignore
#             new_password = serializer.validated_data['new_password'] # type: ignore

#             if not user.check_password(old_password):
#                 return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(new_password)
#             user.save()
#             return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)