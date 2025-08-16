import datetime
import random
import string
import uuid
from django.db import models
from django.forms import ValidationError

from authentication.models import User

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# from business.models import Business
from business.models import BusinessInfo
from media_location.models import Location



ORDER_STATUS=(
        ('created','created'),
        ('accepted','accepted'),
        ('verified','verified'),
        ('complete','complete'),
        
    )


# Create your models here.
class ActivityTime(models.Model):
    preferred_date = models.DateField()
    start_time = models.TimeField()
    stop_time = models.TimeField()
    frequency = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.preferred_date} from {self.start_time} to {self.stop_time} ({self.frequency})"

    def clean(self):
        """
        Ensures stop_time is after start time
        """
        if self.stop_time <= self.start_time:
            raise ValidationError(_('Stop time must be after start time'))

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called on save
        super().save(*args, **kwargs)




class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=30)
    reference_number = models.CharField(max_length=15, unique=True, editable=False)
    completed = models.BooleanField()
    accepted = models.BooleanField()
    payment = models.PositiveIntegerField()
    special_instructions = models.TextField()
    paid = models.BooleanField()
    # services = models.ManyToManyField(Service, related_name='orders')
    business = models.ForeignKey(BusinessInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    location = models.ForeignKey(Location,on_delete=models.CASCADE)
    activity_time = models.ForeignKey(ActivityTime,on_delete=models.CASCADE)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='created')

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Corrected to use Django's timezone utility
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            self.reference_number = f"{timestamp}{random_suffix}"
        super().save(*args, **kwargs)

    # def save(self,*args,**kwargs):
    #     if not self.reference_number:
    #         timestamp = datetime.timezone.now().strftime('%Y%m%d%H%M%S')
    #         random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    #         self.reference_number = f"{timestamp}{random_suffix}"
    #     super().save(*args, **kwargs)
    def __str__(self):
        return self.reference_number


class Instruction(models.Model):
    order = models.ForeignKey(Order, related_name='instructions', on_delete=models.CASCADE)
    complete = models.BooleanField()
    instruction = models.TextField()

