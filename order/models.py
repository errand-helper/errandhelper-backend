from django.db import models

# Create your models here.
# order[icon:orbit,color:red]{
#   id bigint pk
#   reference_number CharField
#   completed BooleanField
#   accepted BooleanField
#   payment CharField
#   special_instructions TextField
#   paid BooleanField
#   services ManyToManyField
#   business_id ForeignKey
#   user_id ForeignKey
#   location_id ForeignKey
#   activity_time_id ForeignKey
#   order_status CharField
# }