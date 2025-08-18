import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    name = models.CharField(max_length=255,unique=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name
























# import uuid
# from django.db import models

# # from authentication.models import User
# # from business.models import Business

# # Create your models here.

# # create and get category - only user with staff privilege can add category
# # get category detail, update and delete the category - only user who added the category can update and  delete the category

# class Category(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
#     # user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
#     name = models.CharField(max_length=255,unique=True)

#     class Meta:
#         verbose_name_plural = "Categories"

#     def __str__(self):
#         return self.name

# # class Service(models.Model):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
# #     user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
# #     category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True, related_name="services")
# #     name = models.CharField(max_length=255)

# #     def __str__(self):
# #         return self.name
    
# # class BusinessCategory(models.Model):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
# #     user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
# #     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="business_services")
# #     # services = models.ManyToManyField(Service, related_name="business_services")

# #     def __str__(self):
# #         return self.business