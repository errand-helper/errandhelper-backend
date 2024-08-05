import uuid
from django.db import models

from authentication.models import User

# Create your models here.

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=200)
    activation_fee = models.CharField(max_length=10)

    # service = models.ManyToManyField(Service,related_name='business')

    def __str__(self):
        return self.business_name