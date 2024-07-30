from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from authentication.serializers import LoginSerializer, RegistrationSerializer
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.authentication import TokenAuthentication
# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    # authentication_classes = []

    def post(self, request):
        # user = request.data.get("user", {})
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # serializer.save()
        # refresh = RefreshToken.for_user(user)
        # # print(refresh)
        # tokens = {
        #     'refresh':str(refresh),
        #     'access':str(refresh.access_token)
        # }
        return Response(
            {'user':serializer.data}, 
            status=status.HTTP_201_CREATED)
    
    
class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)

        # Get the validated data, which includes the tokens
        validated_data = serializer.validated_data

        # print(validated_data)

        return Response(
            {
                # 'user': {
                    'id': validated_data['id'],
                    'email': validated_data['email'],
                    'access': validated_data['access'],
                    'refresh': validated_data['refresh'],


                # },
            },
            status=status.HTTP_200_OK
        )