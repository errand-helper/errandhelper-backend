import django_filters
from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.exceptions import ValidationError
from .models import BusinessInfo, FrequentlyAskedQuestion, Service, ServiceArea
from .serializers import AvailabilitySerializer, BusinessInfoSerializer, FrequentlyAskedQuestionSerializer, PublicBusinessDetailLiteSerializer, PublicBusinessDetailSerializer, PublicBusinessListSerializer, ServiceAreaSerializer, ServiceSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q
from rest_framework.views import APIView
from django.db.models import Count

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class BusinessInfoFilter(django_filters.FilterSet):
    categories = django_filters.CharFilter(method="filter_categories")
    service_areas = django_filters.CharFilter(method="filter_service_areas")

    class Meta:
        model = BusinessInfo
        fields = []

    def filter_categories(self, queryset, name, value):
        category_ids = [v.strip() for v in value.split(",") if v.strip()]
        if category_ids:
            queryset = queryset.filter(
                user__services__category__id__in=category_ids
            )
        return queryset.distinct()

    def filter_service_areas(self, queryset, name, value):
        areas = [v.strip() for v in value.split(",") if v.strip()]
        if areas:
            queryset = queryset.filter(
                user__service_area__area_name__in=areas
            )
        return queryset.distinct()


# class BusinessInfoFilter(django_filters.FilterSet):
#     # Allow filtering by service category name or ID
#     categories = django_filters.BaseInFilter(
#         field_name="user__services__category__id", lookup_expr="in"
#     )

#     # Allow filtering by service area name
#     service_areas = django_filters.BaseInFilter(
#         field_name="user__service_area__area_id", lookup_expr="in"
#     )

#     class Meta:
#         model = BusinessInfo
#         fields = []  # Leave empty to avoid DRF errors


class BusinessInfoViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 15 * 2,key_prefix='businessinfo'))
    def list(self,request,*args,**kwargs):
        return super().list(request,*args,**kwargs)

    def get_queryset(self):
        # User can only see their own business
        # import time
        # time.sleep(2)
        return BusinessInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure only one BusinessInfo per user
        if BusinessInfo.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a BusinessInfo.")
        serializer.save(user=self.request.user)


# class BusinessList(generics.ListAPIView):
#     queryset = BusinessInfo.objects.all()
#     serializer_class = BusinessInfoSerializer
#     permission_classes = [permissions.AllowAny]


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


class PublicBusinessListViewSet(viewsets.ReadOnlyModelViewSet):
    # queryset = BusinessInfo.objects.all()
    queryset = BusinessInfo.objects.all().distinct()
    serializer_class = PublicBusinessListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["business_name", "business_tagline"]
    filterset_class = BusinessInfoFilter

    @method_decorator(cache_page(60 * 15 * 2,key_prefix='business_list'))
    def list(self,request,*args,**kwargs):
        return super().list(request,*args,**kwargs)


class BusinessStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Count businesses per category
        category_stats = (
            Service.objects.values("category__id", "category__name")
            .annotate(business_count=Count("user__business_info", distinct=True))
            .order_by("category__name")
        )
        categories = [
            {
                "id": c["category__id"],
                "name": c["category__name"],
                "business_count": c["business_count"],
            }
            for c in category_stats
        ]

        # Count businesses per service area
        service_area_stats = (
            ServiceArea.objects
            .annotate(business_count=Count("user__business_info", distinct=True))
            .values("id", "area_name", "business_count")
            .order_by("area_name")
        )

        service_areas = [
            {
                "id": a["id"],
                "area_name": a["area_name"],
                "business_count": a["business_count"],
            }
            for a in service_area_stats
        ]

        return Response({
            "categories": categories,
            "service_areas": service_areas,
        })



class AvailabilityView(generics.UpdateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the BusinessInfo for the logged-in user only
        try:
            return BusinessInfo.objects.get(user=self.request.user)
        except BusinessInfo.DoesNotExist:
            raise ValidationError("BusinessInfo not found for this user.")




class PublicBusinessDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessInfo.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PublicBusinessDetailSerializer
        return PublicBusinessListSerializer
    
class PublicBusinessDetailLiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessInfo.objects.filter(available=True)
    serializer_class = PublicBusinessDetailLiteSerializer


# class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = BusinessInfo.objects.all()
#     serializer_class = BusinessInfoSerializer
#     permission_classes = [permissions.AllowAny]
