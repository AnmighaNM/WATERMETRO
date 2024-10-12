from django.db import models
from WebAdmin.models import *
from Guest.models import *
import random
import string
from StationMaster.models import *

# Create your models here.

class tbl_ticketbooking(models.Model):
    date = models.DateField()
    ticket_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    adults_count = models.CharField(max_length=20)
    childrens_count = models.CharField(max_length=20)
    book_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Use DecimalField for monetary values
    service = models.ForeignKey(tbl_services, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.IntegerField(default=0)  # False for pending, True for completed
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Store payment ID if available
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = 'TN-' + ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)
    status=models.IntegerField(default=0)
    sentiment_score = models.FloatField(default=0)  # Field for sentiment score

    def __str__(self):
        return self.title

class tbl_eventbooking(models.Model):
    event_date = models.DateField()
    event_startpoint = models.ForeignKey(tbl_place, on_delete=models.CASCADE, related_name='event_startpoints')
    event_endpoint = models.ForeignKey(tbl_place, on_delete=models.CASCADE, related_name='event_endpoints')
    event_starttime = models.TimeField(default=time(0, 0))  # Default to 00:00:00
    duration = models.DurationField(null=True, blank=True)  # Store duration as a time period
    event_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    adult_count = models.CharField(max_length=20)
    children_count = models.CharField(max_length=20)
    boat_deck = models.CharField(max_length=50,default='1')
    event_type = models.ForeignKey(tbl_eventtype, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assign = models.ForeignKey(tbl_boat, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=0)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Store payment ID if available
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.event_number:
            self.event_number = 'ETN-' + ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)