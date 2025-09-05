from django.urls import path

from .views import CategoryDetailView, CategoryListCreateAPIView, LocationDetailView, LocationListCreateAPIView

urlpatterns = [
    # path('register/', RegisterBusiness.as_view()),
    path('category/', CategoryListCreateAPIView.as_view()),
    path('category/<str:pk>/', CategoryDetailView.as_view()),
    path('location/', LocationListCreateAPIView.as_view()),
    path('location/<str:pk>/', LocationDetailView.as_view()),

    # path('add-service/', ServiceView.as_view()),
    # path('add-service/<str:pk>/', ServiceDetailView.as_view()),

    # path('business/<uuid:business_id>/', ServiceByBusiness.as_view(), name='services-by-business'),


]
