import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from authentication.models import User


class SocialMedia(models.Model):
    facebook = models.URLField(max_length=250,blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    website = models.URLField(blank=True)

class Location(models.Model):
    address = models.CharField(max_length=200)
    town = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=200)

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=255,null=True,default=None)
    bio = models.TextField()
    image = models.ImageField(upload_to="images/profiles",null=True)
    location = models.ForeignKey(Location,related_name="profiles",on_delete=models.CASCADE,null=True,blank=True)
    social_media = models.ForeignKey(SocialMedia,related_name="profiles",on_delete=models.CASCADE,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
    @receiver(post_save,sender=User)
    def create_user_profile(sender,instance,created,**kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
