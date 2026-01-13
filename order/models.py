import random
import string
import uuid
from django.db import models

from authentication.models import User

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from business.models import Service
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
        ('platform', 'Platform'),
        ('mpesa','MPESA')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('funds_held', 'Funds Held'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
        ('paid_out', 'Paid Out'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]


    # STATUS_CHOICES = [
    #     ('pending', 'Pending'),       
    #     ('rejected', 'Rejected'),     
    #     ('in_progress', 'In Progress'),
    #     ('completed', 'Completed'),
    #     ('cancelled', 'Cancelled'),
    # ]

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
    services = models.ManyToManyField(
        Service,
        related_name='errands',
        blank=True
    )

    paid = models.BooleanField(default=False)
    milestones = models.JSONField(default=list, blank=True)

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_errands',
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
    image_url = models.URLField(max_length=500,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.errand.errand_title}"
    
class MpesaTransaction(models.Model):
    TRANSACTION_DIRECTION = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    errand = models.ForeignKey(Errand, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    checkoutRequestID = models.CharField(max_length=100, blank=True)
    merchantRequestID = models.CharField(max_length=100, blank=True)
    mpesaReceiptNumber = models.CharField(max_length=100, blank=True)
    direction = models.CharField(max_length=10, choices=TRANSACTION_DIRECTION)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    rawCallback = models.JSONField(default=dict, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    checkoutId = models.CharField(max_length=100, unique=True, blank=True, null=True)
    mpesaCode = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return f"MpesaTransaction {self.id} - {self.status}"
    


class Escrow(models.Model):
    STATUS_CHOICES = [
        ('holding', 'Holding'),
        ('released', 'Released'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    errand = models.OneToOneField(Errand, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='holding')
    heldAt = models.DateTimeField(auto_now_add=True)
    releasedAt = models.DateTimeField(null=True, blank=True)



class Payout(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    errand = models.ForeignKey(Errand, on_delete=models.CASCADE)
    business = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    mpesaTransaction = models.OneToOneField(
        MpesaTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class Dispute(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    errand = models.OneToOneField(Errand, on_delete=models.CASCADE)
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_at = models.DateTimeField(auto_now_add=True)




class Wallet(models.Model):
    OWNER_TYPE_CHOICES = [
        ('platform', 'Platform'),
        ('business', 'Business'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES)
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner_type', 'owner')




class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('hold', 'Hold'),
        ('release', 'Release'),
        ('refund', 'Refund'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    errand = models.ForeignKey(Errand, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    reference = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)








