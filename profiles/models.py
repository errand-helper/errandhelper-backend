import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from authentication.models import User




class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    # phone_number = models.CharField(max_length=255,null=True,default=None)
    bio = models.TextField()
    image = models.ImageField(upload_to="images/profiles",null=True)
    
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
