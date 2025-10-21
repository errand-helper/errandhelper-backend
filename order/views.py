from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,filters
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from order.models import Errand
from order.serializers import ErrandListMinimalSerializer, ErrandSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.
class ErrandViewSet(viewsets.ModelViewSet):
    queryset = Errand.objects.all()
    serializer_class = ErrandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Also works — same as overriding create() in serializer
        serializer.save(client=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Errand.objects.filter(client=user)
        elif user.role == 'business':
            return Errand.objects.filter(business=user)
        return Errand.objects.none()
    

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

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

    

# class ErrandMinimalViewSet(viewsets.ModelViewSet):
#     queryset = Errand.objects.all()
#     serializer_class = ErrandListMinimalSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ["reference_number"]
#     ordering_fields = ['created_at']
#     filterset_fields = ['status']

#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'client':
#             return Errand.objects.filter(client=user)
#         elif user.role == 'business':
#             return Errand.objects.filter(business=user)
#         return Errand.objects.none()
    
#     def get_queryset(self):
#         return Errand.objects.all().order_by('-created_at')



























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