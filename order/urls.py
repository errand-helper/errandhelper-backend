from django.urls import path,include
from order.views import  ErrandViewSet, InitiatePaymentAPIView, OrderView,ErrandMinimalViewSet, STKStatusAPIView, ReleaseEscrowAPIView, mpesa_callback_view
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'errands', ErrandViewSet, basename='errand')
router.register(r'errand-list', ErrandMinimalViewSet, basename='errand-list')


urlpatterns = [
    path('', include(router.urls)),
    # ---- Client / Angular APIs ----
    path("mpesa/initiate/", InitiatePaymentAPIView.as_view(),name="mpesa-initiate"),
    path("mpesa/status/",STKStatusAPIView.as_view(),name="mpesa-status"),
    # ---- Safaricom Callbacks ----
    path("mpesa/callback/",mpesa_callback_view,name="mpesa-callback"),

    # path('create/<uuid:business_id>/', OrderView.as_view(), name='create-order'),
    path('orders/', OrderView.as_view(), name='order-list-create'),
    path('create-order/<uuid:business_id>/', OrderView.as_view(), name='create-order'),  # If using the business_id approach
    # path('order/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail')

    # Escrow / payouts
    path("escrow/release/", ReleaseEscrowAPIView.as_view(), name="escrow-release"),
    # path("payouts/", PayoutListAPIView.as_view()),

    # # Disputes
    # path("disputes/", DisputeListCreateAPIView.as_view()),
    # path("disputes/<uuid:id>/resolve/", ResolveDisputeAPIView.as_view()),

    # # Wallets (read-only)
    # path("wallets/me/", MyWalletAPIView.as_view()),

]
