from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from .models import BusinessInfo
from .serializers import BusinessInfoSerializer

class BusinessInfoViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # User can only see their own business
        return BusinessInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure only one BusinessInfo per user
        if BusinessInfo.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a BusinessInfo.")
        serializer.save(user=self.request.user)

























# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
# from rest_framework.response import Response
# from rest_framework import status,generics,viewsets

# from business.models import Business, BusinessCategory
# from rest_framework.decorators import action

# from .models import Category
# from .serializers import BusinessCategorySerializer, BusinessRegisterSerializer, BusinessRetrieve

# Create your views here.


# class RegisterBusiness(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = BusinessRegisterSerializer
#     authentication_classes = []

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # serializer.data, 
#         return Response({"details": "Created successfully"},status=status.HTTP_201_CREATED)
    
# class BusinessRetrieveView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = BusinessRegisterSerializer

#     def get_object(self):
#         user = self.request.user
#         print(user,'sddddddddddddddd')
#         return Business.objects.get(user=user)

#     def retrieve(self, request, *args, **kwargs):
#         business = self.get_object()
#         serializer = self.serializer_class(business)
#         return Response(serializer.data, status=status.HTTP_200_OK) 
    

# class BusinessDetailView(APIView):
#     def get(self, request, user_id):
#         # Filter business by the given user ID
#         try:
#             business = Business.objects.get(user_id=user_id)
#             # Serialize the business data
#             serializer = BusinessRetrieve(business)
#             # Return the serialized data
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Business.DoesNotExist:
#             # If no business is found for the given user ID
#             return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
    # def get(self, request, business_id):
    #     try:
    #         # Get the business instance by its ID
    #         business = Business.objects.get(id=business_id)
            
    #         # Serialize the business data
    #         serializer = BusinessRetrieve(business)
            
    #         # Return the serialized data
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Business.DoesNotExist:
    #         # Return a 404 response if the business does not exist
    #         return Response({"error": "Business not found."}, status=status.HTTP_404_NOT_FOUND)
    
# class ListBusinesses(APIView):
#     permission_classes = [IsAuthenticated,IsAdminUser]
    
#     def get(self,request,format=None):
#         businesses = Business.objects.all()
#         serializer = BusinessRegisterSerializer(businesses,many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)


# class BusinessCategoryCreateView(generics.ListCreateAPIView):
#     queryset = BusinessCategory.objects.all()
#     serializer_class = BusinessCategorySerializer

# class BusinessCategoryListView(generics.ListAPIView):
#     queryset = BusinessCategory.objects.all()
#     serializer_class = BusinessCategorySerializer

# class BusinessCategoryUpdateView(generics.RetrieveUpdateAPIView):
#     queryset = BusinessCategory.objects.all()
#     serializer_class = BusinessCategorySerializer


# class BusinessCategoryViewSet(viewsets.ModelViewSet):
#     queryset = BusinessCategory.objects.all()
#     serializer_class = BusinessCategorySerializer

#     @action(detail=True, methods=['post'], url_path='remove-category')
#     def remove_category(self, request, pk=None):
#         business_category = self.get_object()
#         category_id = request.data.get('category_id')

#         try:
#             # Retrieve the category to remove
#             category = Category.objects.get(id=category_id)
#         except Category.DoesNotExist:
#             return Response(
#                 {"error": "Category not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Remove the category from the ManyToMany relationship
#         business_category.categories.remove(category)

#         return Response(
#             {"message": "Category removed successfully."},
#             status=status.HTTP_200_OK
#         ) 