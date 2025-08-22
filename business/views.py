from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.exceptions import ValidationError
from .models import BusinessInfo, FrequentlyAskedQuestion, Service, ServiceArea
from .serializers import BusinessInfoSerializer, FrequentlyAskedQuestionSerializer, ServiceAreaSerializer, ServiceSerializer
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
# from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Optional: Custom paginator


class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


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


class BusinessList(generics.ListAPIView):
    queryset = BusinessInfo.objects.all()
    serializer_class = BusinessInfoSerializer
    permission_classes = [permissions.AllowAny]


class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessInfo.objects.all()
    serializer_class = BusinessInfoSerializer
    permission_classes = [permissions.AllowAny]

    # BusinessInfoSerializer ,ServiceSerializer,ServiceAreaSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ServicePagination

    # ✅ Add filters, search, and ordering
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]

    # ✅ Filter services by category
    filterset_fields = ['category']

    # ✅ Searchable fields
    search_fields = ['name', 'category__name']

    # ✅ Orderable fields
    ordering_fields = ['name', 'price_from', 'price_to']
    ordering = ['name']

    def get_queryset(self):
        # Only return services for the logged-in user
        return Service.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign logged-in user
        serializer.save(user=self.request.user)


class ServiceAreaViewSet(viewsets.ModelViewSet):
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return services for the logged-in user
        return ServiceArea.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data

        # Check if the incoming data is a list (bulk create)
        if isinstance(data, list):
            # Attach the user to each item
            for item in data:
                item["user"] = request.user.id

            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return Response({
                "message": "Service area created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # Handle single object creation
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "message": "Service area created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save(user=self.request.user)


class FrequentlyAskedQuestionViewSet(viewsets.ModelViewSet):
    queryset = FrequentlyAskedQuestion.objects.all()
    serializer_class = FrequentlyAskedQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
