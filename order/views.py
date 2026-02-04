from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,filters
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from order.models import Errand
from order.mpesa_stk import (
    MpesaSTKService,
    PaymentAlreadyCompletedError,
    PaymentInProgressError,
)
from order.serializers import ErrandListMinimalSerializer, ErrandSerializer, InitiateMpesaPaymentSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .mpesa_callback import MpesaCallbackService
import json
import logging

from rest_framework.permissions import BasePermission
from order.utils import format_phone_number



logger = logging.getLogger(__name__)

class IsErrandOwnerOrBusiness(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.client == request.user or
            obj.business == request.user
        )


# Create your views here.
class ErrandViewSet(viewsets.ModelViewSet):
    queryset = Errand.objects.all()
    serializer_class = ErrandSerializer
    permission_classes = [permissions.IsAuthenticated,IsErrandOwnerOrBusiness]

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')

        # Prevent user from assigning errand to themselves
        if self.request.user == business:
            raise ValidationError({"error": "You cannot assign yourself an errand."})
        
        # if self.request.user.role != 'client':
        #     raise ValidationError({"error": "Only clients can create errands."})

        serializer.save(client=self.request.user)

    def perform_update(self, serializer):
        business = serializer.validated_data.get('business')

        if business and self.request.user == business:
            raise ValidationError({
                "error": "You cannot assign yourself an errand."
            })

        serializer.save()
    

    # def perform_update(self, serializer):
    #     business = serializer.validated_data.get('business')

    #     # Prevent user from assigning errand to themselves
    #     if self.request.user == business:
    #         raise ValidationError({"error": "You cannot assign yourself an errand."})

    #     serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Errand.objects.filter(client=user)
        elif user.role == 'business':
            return Errand.objects.filter(business=user)
        return Errand.objects.none()
    
     # ✅ Custom action to accept errand
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        errand = self.get_object()

        # Only the assigned business can accept
        if request.user != errand.business:
            return Response({'error': 'You are not authorized to accept this errand.'},
                            status=status.HTTP_403_FORBIDDEN)
        errand.status = 'in_progress'
        errand.save()

        # serializer = self.get_serializer(errand) 
        # serializer.data
        return Response({'success': 'You have successfully accepted the errand state.'}, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        errand = self.get_object()

        if request.user != errand.business:
            return Response({'error': 'You are not authorized to reject this errand.'},
                            status=status.HTTP_403_FORBIDDEN)

        errand.status = 'rejected'
        errand.save()

        # serializer = self.get_serializer(errand)
        # serializer.data
        return Response({'success': 'You have successfully rejected the errand.'}, status=status.HTTP_200_OK)
    
    # ✅ Complete errand (business or client)
    # Use url_path='completed' to match frontend calling /completed/
    @action(detail=True, methods=['post', 'get'], permission_classes=[permissions.IsAuthenticated], url_path='completed')
    def complete(self, request, pk=None):
        errand = self.get_object()

        # For GET, just return current data to avoid 404s from accidental navigations
        if request.method == 'GET':
            return Response(self.get_serializer(errand).data, status=status.HTTP_200_OK)

        if request.user not in [errand.client, errand.business]:
            return Response({'error': 'You are not authorized to complete this errand.'},
                            status=status.HTTP_403_FORBIDDEN)

        if errand.status != 'in_progress':
            return Response({'error': 'Only errands in progress can be completed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        errand.status = 'completed'
        errand.save()
        return Response({'success': 'You have successfully completed the errand.'}, status=status.HTTP_200_OK)

    # ✅ Cancel errand (client only)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        errand = self.get_object()
        if request.user != errand.client:
            return Response({'error': 'You are not authorized to cancel this errand.'},
                            status=status.HTTP_403_FORBIDDEN)

        if errand.status not in ['pending', 'in_progress']:
            return Response({'error': 'Only pending or active errands can be cancelled.'},
                            status=status.HTTP_400_BAD_REQUEST)

        errand.status = 'cancelled'
        errand.save()
        return Response({'success': 'You have successfully cancelled the errand.'}, status=status.HTTP_200_OK)
    

class ErrandMinimalViewSet(viewsets.ModelViewSet):
    serializer_class = ErrandListMinimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # default ordering
    filterset_fields = ['status']  # ✅ enables ?status=pending etc.

    def get_queryset(self):
        user = self.request.user
        queryset = Errand.objects.all()
        if user.role == 'client':
            queryset = queryset.filter(client=user)
        elif user.role == 'business':
            queryset = queryset.filter(business=user)

        # always return latest first
        return queryset.order_by('-created_at')
    



class InitiatePaymentAPIView(APIView):
    def post(self, request):
        serializer = InitiateMpesaPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            errand = Errand.objects.get(id=serializer.validated_data['errand_id'])
        except Errand.DoesNotExist:
            return Response(
                {"detail": "Errand not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            phone = format_phone_number(serializer.validated_data['phone_number'])
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = serializer.validated_data['amount']

        service = MpesaSTKService()
        try:
            response = service.initiate_payment(
                errand=errand,
                phone_number=phone,
                amount=amount,
            )
        except PaymentAlreadyCompletedError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )
        except PaymentInProgressError as exc:
            return Response(
                {
                    "detail": str(exc),
                    "checkout_request_id": exc.checkout_request_id,
                },
                status=status.HTTP_409_CONFLICT,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(response, status=status.HTTP_200_OK)   

# @csrf_exempt
# def mpesa_callback_view(request):
#     payload = json.loads(request.body)
#     MpesaCallbackService().process_stk_callback(payload)

#     return JsonResponse({
#         "ResultCode": 0,
#         "ResultDesc": "Accepted"
#     })

# @csrf_exempt
# def mpesa_callback_view(request):
#     try:
#         payload = json.loads(request.body)
#         MpesaCallbackService().process_stk_callback(payload)
#     except Exception as e:
#         # Log but never reject Safaricom
#         logger.exception("M-Pesa callback processing failed")

#     return JsonResponse({
#         "ResultCode": 0,
#         "ResultDesc": "Accepted"
#     })

@csrf_exempt
def mpesa_callback_view(request):
    if request.method != "POST":
        return JsonResponse(
            {"detail": "Method not allowed."},
            status=405,
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.exception("Invalid M-Pesa callback payload body")
        # Always acknowledge so Safaricom does not keep retrying malformed payloads.
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    try:
        MpesaCallbackService().process_stk_callback(payload)
    except Exception:
        logger.exception("M-Pesa callback processing failed")
        # Always acknowledge receipt and handle retries/idempotency internally.
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })



class STKStatusAPIView(APIView):
    def post(self, request):
        checkout_id = request.data.get("checkout_request_id")
        service = MpesaSTKService()
        try:
            payment_status = service.query_status(checkout_id)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(payment_status, status=status.HTTP_200_OK)






























class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self,request,*args,**kwargs):
        business_id = kwargs.get('business_id')
        business = ''
        if not business_id:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     # Retrieve the Business instance
        #     business = Business.objects.get(id=business_id)
        # except Business.DoesNotExist:
        #     return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter orders by the business instance
        orders = Errand.objects.filter(business=business)
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # business = self.request.business
        # order = Order.objects.all(business=business)
        # serializer = self.serializer_class(order,many=True)
        # return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request,*args,**kwargs):
        business_id = kwargs.get('business_id')
        print(business_id)

        if not business_id:
            return Response({'error':'Business ID is required'},status=status.HTTP_400_BAD_REQUEST)
        business_instance = ''
        # try:
        #     business_instance = Business.objects.get(id=business_id)
        # except Business.DoesNotExist:
        #     return Response({'error':'Business not found'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data,context={
            'request':request,'business_instance':business_instance
        })

        print(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
