
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from authentication.serializers import ChangePasswordSerializer, LoginSerializer, RegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

    

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
        # } {'user':serializer.data},
        return Response("Created successfully",status=status.HTTP_201_CREATED)
    
    
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
                    'id': validated_data['id'], # type: ignore
                    'email': validated_data['email'], # type: ignore
                    'user_type': validated_data['user_type'], # type: ignore
                    'access': validated_data['access'], # type: ignore
                    'refresh': validated_data['refresh'], # type: ignore


                # },
            }, # type: ignore
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password'] # type: ignore
            new_password = serializer.validated_data['new_password'] # type: ignore

            if not user.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)