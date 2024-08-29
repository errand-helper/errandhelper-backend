from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from business.models import Business
from order.models import Order
from order.serializers import OrderSerializer

# Create your views here.
class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self,request,*args,**kwargs):
        business_id = kwargs.get('business_id')

        if not business_id:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the Business instance
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter orders by the business instance
        orders = Order.objects.filter(business=business)
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
        
        try:
            business_instance = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({'error':'Business not found'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=request.data,context={
            'request':request,'business_instance':business_instance
        })

        print(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)