from django.urls import path

from .views import BusinessProfileListView, ProfileCreateView, ProfileRetrieveView, ProfileUpdateView

urlpatterns = [
    path('',ProfileRetrieveView.as_view()),
    path('create/', ProfileCreateView.as_view()),
    path('update/', ProfileUpdateView.as_view()),
    path("profiles/", BusinessProfileListView.as_view(), name="business-profile-list"),

]