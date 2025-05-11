from django.db import models
from django.utils.timezone import now
from administrator.models import *
from seller.models import *

class DeliveryAgent(models.Model):
    agent = models.OneToOneField(User, on_delete=models.CASCADE, related_name="delivery_agent")
    address = models.TextField()
    pancard_no = models.CharField(max_length=10, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    license = models.CharField(max_length=11, blank=True, null=True)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery Agent Details for {self.agent.username}"

