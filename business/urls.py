from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AvailabilityView, BusinessInfoViewSet, BusinessStatsView, FrequentlyAskedQuestionViewSet, PublicBusinessDetailLiteViewSet, PublicBusinessDetailViewSet, PublicBusinessListViewSet, ServiceAreaViewSet, ServiceViewSet
from business import views

router = DefaultRouter()
router.register(r'business', BusinessInfoViewSet, basename='businessinfo')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-areas', ServiceAreaViewSet, basename='service-areas')
router.register(r'frequently-asked-question', FrequentlyAskedQuestionViewSet, basename='frequently-asked-question')
router.register(r'business-list', PublicBusinessListViewSet, basename='public-businesses')
router.register(r'business-details', PublicBusinessDetailViewSet, basename='public-business-details')
router.register(r'business-lite-details', PublicBusinessDetailLiteViewSet, basename='public-business-lite-details')


urlpatterns = [
    path('', include(router.urls)),
     path("stats/", BusinessStatsView.as_view(), name="business-stats"),
     path("availability/", AvailabilityView.as_view(), name="availability"),
]










