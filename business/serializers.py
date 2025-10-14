from rest_framework import serializers
from .models import BusinessInfo, FrequentlyAskedQuestion, Service, ServiceArea, SocialMedia


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = '__all__'


class BusinessInfoSerializer(serializers.ModelSerializer):
    social_links = SocialMediaSerializer(required=False)

    class Meta:
        model = BusinessInfo
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        social_data = validated_data.pop('social_links', None)
        if social_data:
            social = SocialMedia.objects.create(**social_data)
            validated_data['social_links'] = social
        return BusinessInfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        social_data = validated_data.pop('social_links', None)
        if social_data:
            if instance.social_links:
                for attr, value in social_data.items():
                    setattr(instance.social_links, attr, value)
                instance.social_links.save()
            else:
                instance.social_links = SocialMedia.objects.create(
                    **social_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Service
        fields = '__all__'


class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = '__all__'


class FrequentlyAskedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        # fields = '__all__'
        fields = [
            'id','question','answer'
        ]


class PublicBusinessListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    service_areas = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    # frequently_asked_questions = serializers.SerializerMethodField()
    business_logo = serializers.SerializerMethodField()
    # social_links = serializers.SerializerMethodField()


    class Meta:
        model = BusinessInfo
        fields = [
            "id",
            "business_name",
            "business_logo",
            "user",
            # "business_phone",
            # "business_email",
            "business_tagline",
            # "business_description",
            "category",
            "service_areas",
            "services",
            # "frequently_asked_questions",
            "available",
            # "social_links"
        ]

    def get_category(self, obj):
        # Get distinct categories from related services
        return list(obj.user.services.values_list("category__name", flat=True).distinct())

    def get_service_areas(self, obj):
        # Get distinct service areas
        return list(obj.user.service_area.values_list("area_name", flat=True).distinct())

    def get_services(self, obj):
        services = obj.user.services.values("id", "name","category","price_type","price_from","price_to").distinct()
        return list(services)
    
    # def get_frequently_asked_questions(self, obj):
    #     faqs = obj.user.frequently_asked_question.values("id", "question", "answer").distinct()
    #     return list(faqs)
    
    def get_business_logo(self, obj):
        request = self.context.get("request")
        if obj.business_logo:
            return request.build_absolute_uri(obj.business_logo.url)
        return None
    
    # def get_social_links(self, obj):
    #     if obj.social_links:
    #         return {
    #             "facebook": obj.social_links.facebook,
    #             "instagram": obj.social_links.instagram,
    #             "twitter": obj.social_links.twitter,
    #             "linkedin": obj.social_links.linkedin,
    #             "website": obj.social_links.website,
    #         }
    #     return None


class PublicBusinessDetailSerializer(serializers.ModelSerializer):
    social_links = SocialMediaSerializer()
    services = ServiceSerializer(source="user.services", many=True)
    service_area = ServiceAreaSerializer(source="user.service_area", many=True)
    frequently_asked_question = FrequentlyAskedQuestionSerializer(
        source="user.frequently_asked_question", many=True
    )
    class Meta:
        model = BusinessInfo
        fields = "__all__"

class PublicBusinessDetailLiteSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(source="user.services", many=True)
    class Meta:
        model = BusinessInfo
        fields = [
            "id",
            "business_name",
            "business_logo",
            "user",
            "available",
            "services",
        ]


class CategoryStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    business_count = serializers.IntegerField()


class ServiceAreaStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    area_name = serializers.CharField()
    business_count = serializers.IntegerField()


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = ["available"]

