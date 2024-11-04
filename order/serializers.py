from rest_framework import serializers

from business.models import Location
from business.serializers import LocationSerializer
from order.models import ActivityTime, Instruction, Order
# from profiles.serializers import LocationSerializer
# from service.models import Service
# from service.serializers import ServiceSerializer


class ActivityTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTime
        fields = [
            'preferred_date','start_time','stop_time','frequency'
        ]

    def validate(self, attrs):
        """Ensure stop_time is after start_time"""
        if attrs['stop_time'] <= attrs['start_time']:
            raise serializers.ValidationError('Stop time must be after start time')
        return super().validate(attrs)
    
# serializers.py



class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ['complete', 'instruction']

class OrderSerializer(serializers.ModelSerializer):
    instructions = InstructionSerializer(many=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    business_details = serializers.SerializerMethodField(read_only=True)
    # services_details = serializers.SerializerMethodField(read_only=True)

    location = LocationSerializer()
    activity_time = ActivityTimeSerializer()

    class Meta:
        model = Order
        fields = [
            'id', 'reference_number', 'instructions', 'completed', 'accepted', 
            'payment', 'paid', 
            'location', 'activity_time', 'order_status','user_details','business_details'
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
        activity_time_instance = ActivityTime.objects.create(**activity_time_data)
        
        # Create the order instance
        order = Order.objects.create(
            user=user_instance,
            business=business_instance,
            location=location_instance,
            activity_time=activity_time_instance,
            **validated_data
        )

        # Create instructions related to the order
        for instruction_data in instructions_data:
            Instruction.objects.create(order=order, **instruction_data)

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
