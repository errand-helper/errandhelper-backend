from django.urls import path

from .views import RegisterBusiness 

urlpatterns = [
    path('register/', RegisterBusiness.as_view()),
    # path('', CategoryListCreateAPIView.as_view()),

    # path('profile/', BusinessProfileView.as_view()),
    # path('profile/<str:pk>/', BusinessDetailRetrieveProfile.as_view()),

    # path('service-category/', ServiceCategoryView.as_view()),
    # path('service-category/<str:pk>/', ServiceCategoryDetailView.as_view()),

    # path('add-service/', ServiceView.as_view()),
    # path('add-service/<str:pk>/', ServiceDetailView.as_view()),


]