from django.urls import path,include
from order.views import  ErrandViewSet, OrderView,ErrandMinimalViewSet
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'errands', ErrandViewSet, basename='errand')
router.register(r'errand-list', ErrandMinimalViewSet, basename='errand-list')


urlpatterns = [
#     path('create', OrderView.as_view()),
  path('', include(router.urls)),
    # path('create/<uuid:business_id>/', OrderView.as_view(), name='create-order'),
    path('orders/', OrderView.as_view(), name='order-list-create'),
    path('create-order/<uuid:business_id>/', OrderView.as_view(), name='create-order'),  # If using the business_id approach
    # path('order/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail')

]