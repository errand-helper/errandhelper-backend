import uuid
from django.db import models

from authentication.models import User
from service.models import Category

# Create your models here.

class SocialMedia(models.Model):
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    website = models.URLField(blank=True)

class Location(models.Model):
    address = models.CharField(max_length=200,blank=True)
    town = models.CharField(max_length=200,blank=True)
    location = models.CharField(max_length=200,blank=True)
    city = models.CharField(max_length=200,blank=True)



class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="business")
    business_name = models.CharField(max_length=255,unique=True)
    registration_number = models.CharField(max_length=200,unique=True)

    location = models.ForeignKey(Location,related_name="business",on_delete=models.CASCADE,null=True,blank=True)
    social_media = models.ForeignKey(SocialMedia,related_name="business",on_delete=models.CASCADE,null=True,blank=True)

    # activation_fee = models.CharField(max_length=10)

    def __str__(self):
        return self.business_name
    

class BusinessCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    business = models.ForeignKey(Business,on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='business')





