from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from order.models import Errand
from order.serializers import ErrandSerializer, OrderSerializer
from rest_framework.parsers import MultiPartParser, FormParser


# Create your views here.
class ErrandViewSet(viewsets.ModelViewSet):
    queryset = Errand.objects.all()
    serializer_class = ErrandSerializer
    permission_classes = [permissions.IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

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
    

# class ErrandViewSet(viewsets.ModelViewSet):
#     queryset = Errand.objects.all()
#     serializer_class = ErrandSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=True, methods=['post'])
#     def respond(self, request, pk=None):
#         """Business accepts or rejects an errand."""
#         errand = self.get_object()
#         if request.user != errand.business:
#             return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

#         decision = request.data.get('decision')
#         if decision not in ['accepted', 'rejected']:
#             return Response({'error': 'Invalid decision'}, status=status.HTTP_400_BAD_REQUEST)

#         errand.status = decision
#         errand.save()
#         return Response({'message': f'Errand {decision} successfully.'})




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