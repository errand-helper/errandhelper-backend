from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import BusinessCategoryCreateView, BusinessCategoryUpdateView, BusinessCategoryViewSet, BusinessDetailView, BusinessRetrieveView, ListBusinesses, RegisterBusiness

router = DefaultRouter()
router.register(r'business-categories', BusinessCategoryViewSet)




urlpatterns = [
    path('register/', RegisterBusiness.as_view()),
    path('', ListBusinesses.as_view()),
    path('<uuid:user_id>/', BusinessDetailView.as_view(), name='business-detail'),
    path('business-categories/', BusinessCategoryCreateView.as_view(), name='business-category-create'),
    path('business-categories/<uuid:pk>/', BusinessCategoryUpdateView.as_view(), name='business-category-update'),
    path('', include(router.urls)),
    path('details/',BusinessRetrieveView.as_view()),

    # path('business-categories/<uuid:pk>/delete/', BusinessCategoryDeleteView.as_view(), name='business-category-delete'),

    # path('', CategoryListCreateAPIView.as_view()),

    # path('profile/', BusinessProfileView.as_view()),
    # path('profile/<str:pk>/', BusinessDetailRetrieveProfile.as_view()),

    # path('service-category/', ServiceCategoryView.as_view()),
    # path('service-category/<str:pk>/', ServiceCategoryDetailView.as_view()),

    # path('add-service/', ServiceView.as_view()),
    # path('add-service/<str:pk>/', ServiceDetailView.as_view()),


]
