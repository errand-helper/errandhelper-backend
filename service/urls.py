from django.urls import path

from .views import CategoryListCreateAPIView 

urlpatterns = [
    # path('register/', RegisterBusiness.as_view()),
    path('category/', CategoryListCreateAPIView.as_view()),



]