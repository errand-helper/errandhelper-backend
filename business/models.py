import uuid
from django.db import models

from authentication.models import User
from service.models import Category

# Create your models here.

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="business")
    business_name = models.CharField(max_length=255,unique=True)
    registration_number = models.CharField(max_length=200,unique=True)

    class Meta:
        verbose_name_plural = "Businesses"


    def __str__(self):
        return self.business_name
    

class BusinessCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    business = models.ForeignKey(Business,on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='business')





