from rest_framework import serializers

from .models import Category, Service


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =[
            'id','name'
        ]

class ServiceSerializer(serializers.ModelSerializer):
    # categories = CategorySerializer(many=True, read_only=True)
    name = serializers.CharField()
    # business = serializers.CharField(source="business.business_name",read_only=True)

    # category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, many=True
    )

    class Meta:
        model = Service
        fields = ['id','name','category_ids','categories']

    def create(self, validated_data):
        # category = validated_data.pop('category')
        category_ids = validated_data.pop('category_ids')
        business = validated_data.pop('business')
        service = Service.objects.create(business=business, **validated_data)
        service.categories.set(category_ids)
        return service