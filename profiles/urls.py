from django.urls import path

from .views import ProfileImageView, ProfileRetrieveView

urlpatterns = [
    # path('register/', RegisterView.as_view()),
    # path('login/', LoginView.as_view()),
    # path('profiles/<uuid:pk>/',ProfileRetrieveAPIView.as_view()),
    # path('users/',AllUserAPIView.as_view()),
    path('',ProfileRetrieveView.as_view()),
    path('image/', ProfileImageView.as_view(), name='profile-image'),


]