from django.db import models

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

    def __str__(self):
        parts = [self.address, self.town, self.city]
        return ", ".join(filter(None, parts)) or "Unnamed Location"