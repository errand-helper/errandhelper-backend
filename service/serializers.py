from rest_framework import serializers

from .models import Category, Service


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields =[
            'id','name'
        ]

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name",read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')

    class Meta:
        model = Service
        fields = ['id','category_id','category_name','name']

    def create(self, validated_data):
        category = validated_data.pop('category')
        service = Service.objects.create(category=category, **validated_data)
        return service