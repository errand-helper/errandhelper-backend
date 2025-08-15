import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('business', 'Business'),
    )
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']  # For createsuperuser

    def __str__(self):
        return self.email



class ClientProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    preferred_contact_method = models.CharField(max_length=50, blank=True)
    service_preferences = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    notification_preferences = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Client Profile - {self.user.username}"
    

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    name = models.CharField(max_length=255,unique=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name
    
class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True, related_name="services")
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    

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

class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name


class BusinessInfo(models.Model):
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    business_name = models.CharField(max_length=255)
    business_email = models.CharField(max_length=255)
    business_phone = models.CharField(max_length=255)
    business_tagline = models.CharField(max_length=255)
    business_description = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True)
    badges = models.ManyToManyField(Badge, blank=True)
    social_links = models.OneToOneField(SocialMedia, on_delete=models.CASCADE, related_name='business_info')

    def __str__(self):
        return self.business_name


class BusinessProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_info = models.OneToOneField(BusinessInfo, on_delete=models.CASCADE, related_name='business_profile')
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='business_profile')
    services = models.ManyToManyField(Service, blank=True)
    def __str__(self):
        return f"Business Profile - {self.business_name}"







# Basic Information

# Location & Business Hours
# Services Offered
# Service Areas
# Frequently Asked Questions
# Insurance & Certifications
















# import uuid
# from django.db import models
# from django.contrib.auth.models import AbstractUser,BaseUserManager
# from django.conf import settings
# from datetime import datetime, timedelta
# import jwt


# class UserTypes(models.TextChoices):
#     CUSTOMER = "CUSTOMER"
#     BUSINESS = "BUSINESS"
#     ADMIN = "ADMIN"
#     SUPER = "SUPER"

# # Create your models here.
# class customUserManager(BaseUserManager):
#     def create_user(self,email,password,**extra_fields):
#         if not email:
#             raise ValueError('Email must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email,**extra_fields)
#         user.set_password(password)
#         user.save()
#         return user
    
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#         return self.create_user(email, password, **extra_fields)
    

# class User(AbstractUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
#     first_name = models.CharField(max_length=200)
#     last_name = models.CharField(max_length=200)
#     id_number = models.CharField(max_length=200)
#     user_type = models.CharField(max_length=50, choices=UserTypes.choices,default=UserTypes.CUSTOMER)
#     email = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)  # type: ignore
#     is_staff = models.BooleanField(default=False)  # type: ignore

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     username = None

#     objects = customUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
    
#     def save(self,*args,**kwargs):
#         if not self.pk:
#             self.user_type = UserTypes.CUSTOMER
#         super().save(*args,**kwargs)