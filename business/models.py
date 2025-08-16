import uuid
from django.db import models

class SocialMedia(models.Model):
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    website = models.URLField(blank=True)

class BusinessInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True)
    business_email = models.CharField(max_length=255, blank=True)
    business_phone = models.CharField(max_length=255, blank=True)
    business_tagline = models.CharField(max_length=255, blank=True)
    business_description = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    social_links = models.OneToOneField(
        SocialMedia,
        on_delete=models.CASCADE,
        related_name='business_info',
        null=True,
        blank=True
    )
    user = models.OneToOneField(
        'authentication.User',  
        on_delete=models.CASCADE,
        related_name='business_info'
    )

    class Meta:
        verbose_name_plural = "Business Information"

    def __str__(self):
        return self.business_name




















# class Business(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
#     user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="business")
#     business_name = models.CharField(max_length=255,unique=True)
#     registration_number = models.CharField(max_length=200,unique=True)

#     class Meta:
#         verbose_name_plural = "Businesses"


#     def __str__(self):
#         return self.business_name
    

# class BusinessCategory(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
#     business = models.ForeignKey(Business,on_delete=models.CASCADE)
#     categories = models.ManyToManyField(Category, related_name='business')





