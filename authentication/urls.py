# accounts/urls.py
from django.urls import path
from .views import RoleView, SignupView, EmailTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', EmailTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('role',RoleView.as_view(),name="role")

    # path('client/profile/', ClientProfileView.as_view(), name='client-profile'),
    # path('business/profile/', BusinessProfileView.as_view(), name='business-profile'),  # Moved to business app
]












# from django.urls import path

# from .views import  ChangePasswordView, LoginView, RegisterView

# urlpatterns = [
#     path('register/', RegisterView.as_view()),
#     path('login/', LoginView.as_view()),
#     path('change-password/', ChangePasswordView.as_view()),
#     # path('profiles/<uuid:pk>/',ProfileRetrieveAPIView.as_view()),
#     # path('users/',AllUserAPIView.as_view()),
#     # path('profile/',UserRetrieveUpdateAPIView.as_view())

# ]