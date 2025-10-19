import random
import string
import uuid
from django.db import models
# from django.forms import ValidationError

from authentication.models import User

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from media_location.models import Location


class Errand(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]

    BUDGET_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('hourly', 'Hourly'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('platform', 'Platform'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),       
        ('accepted', 'Accepted'),     
        ('rejected', 'Rejected'),     
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=100, unique=True, editable=False)
    errand_title = models.CharField(max_length=255)
    descriptions = models.JSONField(default=list, blank=True)
    locations = models.ManyToManyField(Location, related_name='errands')
    start_date = models.DateTimeField()
    stop_date = models.DateTimeField()
    priority = models.CharField(max_length=255, choices=PRIORITY_CHOICES, default='normal')
    budget_type = models.CharField(max_length=255, choices=BUDGET_TYPE_CHOICES, default='fixed')
    budget_amount = models.DecimalField(max_digits=255, decimal_places=2, null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    use_milestones = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    special_instructions = models.TextField(blank=True)
    contact_preference = models.CharField(max_length=50, default='platform')
    agree_terms = models.BooleanField(default=False)
    agree_escrow = models.BooleanField(default=False)
    services = models.JSONField(default=list, blank=True)
    milestones = models.JSONField(default=list, blank=True)

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_errands',
        # limit_choices_to={'role': 'client'}
    )

    business = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_errands',
        limit_choices_to={'role': 'business'}
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            self.reference_number = f"{timestamp}{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.errand_title} ({self.status})"



class ErrandImage(models.Model):
    errand = models.ForeignKey(
        'Errand',
        on_delete=models.CASCADE,
        related_name='images'
    )
    # image = models.ImageField(upload_to='errand_docs/')
    image_url = models.URLField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.errand.errand_title}"
