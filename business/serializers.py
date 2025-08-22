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
                instance.social_links = SocialMedia.objects.create(**social_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class ServiceSerializer(serializers.ModelSerializer):
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
        fields = '__all__'






