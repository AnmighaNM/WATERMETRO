from django.db import models
from WebAdmin.models import *
from datetime import time

# Create your models here.

class tbl_services(models.Model):
    assignboat_boat = models.ForeignKey(tbl_boat, on_delete=models.CASCADE, default=1)  # Assuming 1 is a valid tbl_boat ID
    services_startpoint = models.ForeignKey(tbl_place, on_delete=models.CASCADE, related_name='services_startpoints')
    services_endpoint = models.ForeignKey(tbl_place, on_delete=models.CASCADE, related_name='services_endpoints')
    assignboat_starttime = models.TimeField(default=time(0, 0))  # Default to 00:00:00
    duration = models.DurationField(null=True, blank=True)  # Store duration as a time period
    rate = models.FloatField(default=0.0)
    status = models.IntegerField(default=1)