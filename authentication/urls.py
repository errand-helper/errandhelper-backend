from django.urls import path

from .views import  LoginView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    # path('profiles/<uuid:pk>/',ProfileRetrieveAPIView.as_view()),
    # path('users/',AllUserAPIView.as_view()),
    # path('profile/',UserRetrieveUpdateAPIView.as_view())

]