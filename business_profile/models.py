import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from authentication.models import User
from business.models import Business
from media_location.models import Location, SocialMedia



class BusinessProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.OneToOneField(User,related_name="business_profile",on_delete=models.CASCADE)
    business = models.OneToOneField(Business,related_name="business_profile",on_delete=models.CASCADE,null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    
    phone_number = models.CharField(max_length=255,null=True,default=None)
    bio = models.TextField()
    image = models.ImageField(upload_to="images/profiles",null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    location = models.ForeignKey(Location,related_name="business_profile",on_delete=models.CASCADE,null=True,blank=True)
    social_media = models.ForeignKey(SocialMedia,related_name="business_profile",on_delete=models.CASCADE,null=True,blank=True)


    def __str__(self):
        return self.user.email
    
    # @receiver(post_save,sender=User)
    # def create_user_profile(sender,instance,created,**kwargs):
    #     if created:
    #         BusinessProfile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.user_profile.save()

    
# services = models.ManyToManyField(Category, related_name='business')
    # ratings = models.ManyToManyField(Rating, related_name='business')
    # reviews = models.ManyToManyField(Review, related_name='business')