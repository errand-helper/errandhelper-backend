import os
from rest_framework import serializers

from business.models import Service
from business.serializers import ServiceSerializer
from media_location.models import Location
from media_location.serializers import LocationSerializer
from order.models import Errand, ErrandImage
import boto3
from django.conf import settings
import base64
import uuid


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_S3_REGION_NAME', '')
    )

s3 = get_s3_client()


class ErrandImageSerializer(serializers.ModelSerializer):
    image_base64 = serializers.CharField(write_only=True, required=True)
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = ErrandImage
        fields = ['id', 'image_base64', 'image_url', 'uploaded_at']

    def create(self, validated_data):
        base64_str = validated_data.pop('image_base64')
        if base64_str.startswith('data:'):
            # split metadata and base64 data
            header, base64_data = base64_str.split(';base64,')
        else:
            base64_data = base64_str
        # Decode the image
        file_data = base64.b64decode(base64_data)

        # Generate a unique file name
        file_name = f"errands/{uuid.uuid4()}.jpg"

        # Upload to S3
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_name,
            Body=file_data,
            ContentType='image/jpeg'
        )
    # Construct file URL
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"

        validated_data['image_url'] = image_url
        return super().create(validated_data)



class ErrandSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True) 
    images = ErrandImageSerializer(many=True, required=False)
    start_date = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"], required=False)
    stop_date = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"], required=False)

    service_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Service.objects.all(),
        write_only=True,
        required=False
    )
    
    # For reading (GET)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Errand
        fields = '__all__'
        read_only_fields = ['client']

    def create(self, validated_data):
        locations_data = validated_data.pop('locations', [])
        images_data = validated_data.pop('images', [])
        services_data = validated_data.pop('service_ids', [])

        validated_data.pop('client', None)
        errand = Errand.objects.create(client=self.context['request'].user, **validated_data)

        if services_data:
            errand.services.set(services_data)

        for loc_data in locations_data:
            loc = Location.objects.create(**loc_data)
            errand.locations.add(loc)

        for img_data in images_data:
            img_serializer = ErrandImageSerializer(data=img_data, context=self.context)
            img_serializer.is_valid(raise_exception=True)
            img_serializer.save(errand=errand)

        return errand
    
    


class ErrandListMinimalSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()
    class Meta:
        model = Errand
        fields = ['id','reference_number','status','client_name', 'business_name','created_at','priority']

    def get_client_name(self, obj):
        """Return the full name of the client."""
        if obj.client:
            full_name = f"{obj.client.first_name or ''} {obj.client.last_name or ''}".strip()
            return full_name if full_name else obj.client.email
        return None

    def get_business_name(self, obj):
        """Return the business name from BusinessInfo."""
        if hasattr(obj.business, "business_info"):
            return obj.business.business_info.business_name
        return obj.business.email  # fallback if business_info doesn’t exist
































class OrderSerializer(serializers.ModelSerializer):
    # instructions = InstructionSerializer(many=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    business_details = serializers.SerializerMethodField(read_only=True)
    # services_details = serializers.SerializerMethodField(read_only=True)

    location = LocationSerializer()
    # activity_time = ActivityTimeSerializer()

    class Meta:
        model = Errand
        fields = [
            'id', 'reference_number', 'instructions', 'completed', 'accepted', 
            'payment', 'paid', 
            'location', 'order_status','user_details','business_details'
        ]
        read_only_fields = ['id', 'reference_number']

    def create(self, validated_data):
        request = self.context.get('request')

        user_instance = request.user if request else None
        business_instance = self.context.get('business_instance')

        validated_data.pop('business', None)
        validated_data.pop('user', None)

        location_data = validated_data.pop('location')
        activity_time_data = validated_data.pop('activity_time')
        # services_data = validated_data.pop('services', None)
        instructions_data = validated_data.pop('instructions', None)

        # Create location and activity_time instances
        location_instance = Location.objects.create(**location_data)
        # activity_time_instance = ActivityTime.objects.create(**activity_time_data)
        
        # Create the order instance
        order = Errand.objects.create(
            user=user_instance,
            business=business_instance,
            location=location_instance,
            # activity_time=activity_time_instance,
            **validated_data
        )

        # Create instructions related to the order
        # for instruction_data in instructions_data:
        #     Instruction.objects.create(order=order, **instruction_data)

        # Set services if provided
        # if services_data:
        #     order.services.set(services_data)

        return order
    
    # def get_services_details(self, obj):
    #     return ServiceSerializer(obj.services.all(), many=True).data
    

    def get_user_details(self, obj):
        return {
            "user_id": obj.user.id,
            "first_name":obj.user.first_name,
            "last_name":obj.user.last_name,
            # "bio":obj.user.profile.bio,
            # "city":obj.user.profile.city,
        }
    
    def get_business_details(self, obj):
        return {
           'business_id':obj.business.id,
            'business_name':obj.business.business_name,
            # 'phone_number':obj.business.user.phone_number,
        }



# class InstructionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Instruction
#         fields = ['complete','instruction']


# # serializers.py

# class OrderSerializer(serializers.ModelSerializer):
#     instructions = InstructionSerializer(many=True)
#     user_details = serializers.SerializerMethodField(read_only=True)
#     business_details = serializers.SerializerMethodField(read_only=True)
#     services_details = serializers.SerializerMethodField(read_only=True)

#     location = LocationSerializer()
#     activity_time = ActivityTimeSerializer()

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'reference_number', 'instructions', 'completed', 'accepted', 
#             'payment', 'paid', 'business', 'services', 'user', 
#             'location', 'activity_time', 'services_details', 'order_status','user_details','business_details'
#         ]
#         read_only_fields = ['id', 'reference_number']

#     def create(self, validated_data):
#         request = self.context.get('request')

#         user_instance = request.user if request else None
#         business_instance = self.context.get('business_instance')

#         # Remove business and user from validated_data as they are handled separately
#         validated_data.pop('business', None)
#         validated_data.pop('user', None)

#         location_data = validated_data.pop('location')
#         activity_time_data = validated_data.pop('activity_time')
#         services_data = validated_data.pop('services', None)
#         instructions_data = validated_data.pop('instructions', None)

#         # Create related instances
#         location_instance = Location.objects.create(**location_data)
#         activity_time_instance = ActivityTime.objects.create(**activity_time_data)
        
#         # Create order instance
#         order = Order.objects.create(
#             user=user_instance,
#             business=business_instance,
#             location=location_instance,
#             activity_time=activity_time_instance,
#             **validated_data
#         )

#         # Create instructions
#         for instruction_data in instructions_data:
#             Instruction.objects.create(order=order, **instruction_data)

#         # Set services for order
#         if services_data:
#             order.services.set(services_data)

#         return order

#     def get_services_details(self, obj):
#         return {
#             'user_id': obj.user.id
#         }
    
#     def get_business_details(self, obj):
#         return {
#             'business_id': obj.business.id
#         }


# class OrderSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     instructions = InstructionSerializer(many=True)
#     completed = serializers.BooleanField()
#     accepted = serializers.BooleanField()
#     paid = serializers.BooleanField()
#     payment = serializers.CharField()
#     services = serializers.PrimaryKeyRelatedField(many=True,queryset=Service.objects.all(),required=False)

#     user_details = serializers.SerializerMethodField(read_only=True)
#     business_details = serializers.SerializerMethodField(read_only=True)
#     service_details = serializers.SerializerMethodField(read_only=True)

#     location = LocationSerializer()
#     activity_time = ActivityTimeSerializer()
#     reference_number = serializers.CharField(max_length=200)
#     order_status = serializers.CharField(max_length=200)

#     # order_status =
#     # reference_number

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'reference_number', 'instructions', 'completed', 'accepted', 
#             'payment', 'paid', 'services','location', 'activity_time', 'order_status','user_details','service_details','business_details'
#         ]

    
#     def create(self,validated_data):
#         request = self.context.get('request')

#         user_instance = request.user if request else None
#         business_instance = self.context.get('business_instance')

#         validated_data.pop('business',None)
#         validated_data.pop('user',None)

#         location_data = validated_data.pop('location')
#         activity_time_data = validated_data.pop('activity_time')
#         services_data = validated_data.pop('services',None)
#         instructions_data = validated_data.pop('instructions',None)

#         location_instance = Location.objects.create(**location_data)
#         activity_time_instance = ActivityTime.objects.create(**activity_time_data)
#         order = Order.objects.create(
#             user=user_instance,
#             business=business_instance,
#             location=location_instance,
#             activity_time=activity_time_instance,
#             **validated_data
#             )
        
#         for instructions_data in instructions_data:
#             Instruction.objects.create(order=order,**instructions_data)

#         if services_data:
#             order.services.set(services_data)
#         return order
    

#     def get_services_data(self,obj):
#         return {
#             'user_id':obj.user.id
#         }
    
#     def get_business_details(self,obj):
#         return {
#             'business_id':obj.business.id
#         }
