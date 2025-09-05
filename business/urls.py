from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessInfoViewSet, BusinessList, BusinessStatsView, FrequentlyAskedQuestionViewSet, PublicBusinessViewSet, ServiceAreaViewSet, ServiceViewSet
from business import views

router = DefaultRouter()
router.register(r'business', BusinessInfoViewSet, basename='businessinfo')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-areas', ServiceAreaViewSet, basename='service-areas')
router.register(r'frequently-asked-question', FrequentlyAskedQuestionViewSet, basename='frequently-asked-question')
router.register(r'business-list', PublicBusinessViewSet, basename='public-businesses')


urlpatterns = [
    path('', include(router.urls)),
     path("stats/", BusinessStatsView.as_view(), name="business-stats"),
]










