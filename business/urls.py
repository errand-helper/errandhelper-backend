from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessInfoViewSet, BusinessList, ServiceViewSet
from business import views

router = DefaultRouter()
router.register(r'businesses', BusinessInfoViewSet, basename='businessinfo')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
    path('business-list/', BusinessList.as_view()),
]










