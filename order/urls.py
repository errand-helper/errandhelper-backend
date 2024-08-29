from django.urls import path
from order.views import  OrderView
from . import views


urlpatterns = [
#     path('create', OrderView.as_view()),
  
    # path('create/<uuid:business_id>/', OrderView.as_view(), name='create-order'),
    path('orders/', OrderView.as_view(), name='order-list-create'),
    path('create-order/<uuid:business_id>/', OrderView.as_view(), name='create-order'),  # If using the business_id approach
    # path('order/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail')

]