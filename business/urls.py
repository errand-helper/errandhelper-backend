from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessInfoViewSet, BusinessList, PublicBusinessViewSet, ServiceViewSet
from business import views

router = DefaultRouter()
router.register(r'business', BusinessInfoViewSet, basename='businessinfo')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'business-list', PublicBusinessViewSet, basename='public-businesses')


urlpatterns = [
    path('', include(router.urls)),
    # path('business-list/', BusinessList.as_view()),
]










