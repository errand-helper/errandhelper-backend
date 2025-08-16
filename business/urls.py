from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessInfoViewSet

router = DefaultRouter()
router.register(r'businesses', BusinessInfoViewSet, basename='businessinfo')

urlpatterns = [
    path('', include(router.urls)),
]





# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import BusinessInfoViewSet

# router = DefaultRouter()
# router.register(r'businesses', BusinessInfoViewSet, basename='businessinfo')

# urlpatterns = [
#     path('', include(router.urls)),
# ]





