import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.conf import settings
from datetime import datetime, timedelta
import jwt


class UserTypes(models.TextChoices):
    CUSTOMER = "CUSTOMER"
    BUSINESS = "BUSINESS"
    ADMIN = "ADMIN"
    SUPER = "SUPER"

# Create your models here.
class customUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=200)
    user_type = models.CharField(max_length=50, choices=UserTypes.choices,default=UserTypes.CUSTOMER)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # type: ignore
    is_staff = models.BooleanField(default=False)  # type: ignore

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None

    objects = customUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def save(self,*args,**kwargs):
        if not self.pk:
            self.user_type = UserTypes.CUSTOMER
        super().save(*args,**kwargs)