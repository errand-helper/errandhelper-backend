import uuid
from django.db import models

from service.models import Category



class ServiceArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area_name = models.CharField(max_length=255, blank=True, null=True)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    service_radius = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_length=255,max_digits=8, decimal_places=2, blank=True, null=True)
    longitude = models.DecimalField(max_length=255,max_digits=8,decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(
        'authentication.User',  
        on_delete=models.CASCADE,
        related_name='service_area', blank=True, null=True
    )

    def __str__(self):
        return self.area_name
    

class FrequentlyAskedQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255, blank=True, null=True)
    answer = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(
        'authentication.User',  
        on_delete=models.CASCADE,
        related_name='frequently_asked_question', blank=True, null=True
    )

    def __str__(self):
        return self.question


    
class Service(models.Model):
    PRICE_TYPE_CHOICES = (
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
        ('quote', 'By Quote'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="services")
    name = models.CharField(max_length=255)
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default='quote', blank=True, null=True)
    price_from = models.CharField(max_length=255, blank=True, null=True)
    price_to = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(
        'authentication.User',  
        on_delete=models.CASCADE,
        related_name='services', blank=True, null=True
    )

    def __str__(self):
        return self.name


class SocialMedia(models.Model):
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField()
    website = models.URLField()


class BusinessInfo(models.Model):
    ROLE_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_logo = models.ImageField(upload_to='media/business_logos/', blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True) # 
    business_email = models.CharField(max_length=255, blank=True)
    business_phone = models.CharField(max_length=255, blank=True)
    business_tagline = models.CharField(max_length=255, blank=True)
    business_description = models.CharField(max_length=255, blank=True)
    # registration_number = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    registration_number = models.CharField(max_length=100, blank=True, null=True) 
    kra_pin = models.CharField(max_length=20, blank=True, null=True) # can be changed to tax pin for world wide expansion
    tax_compliance = models.FileField(upload_to="business_docs/", blank=True, null=True)  # PDF/Images Tax Compliance + License
    license = models.FileField(upload_to="business_docs/", blank=True, null=True)  # PDF/Images Tax Compliance + License
    verification_status = models.CharField(max_length=10, choices=ROLE_CHOICES,default='pending',blank=True, null=True)
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
    available = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = "Business Information"

    def __str__(self):
        return self.business_name





# System cross-checks against:
# BRS Portal / eCitizen (for registration number).
# KRA iTax (for PIN).
# If matches, system auto-sets is_verified = True.
# If not, flag for manual admin review.
# (BRS & KRA APIs are not public, so you might need partnerships or scraping — most startups in KE still do manual checks first.)









