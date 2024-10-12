from django.db import models
from django.conf import settings

# Create your models here.

class tbl_district(models.Model):
    district_name = models.CharField(max_length=100)
    status = models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)

    def __str__(self):
        return self.district_name

class tbl_place(models.Model):
    place_name = models.CharField(max_length=100)
    district = models.ForeignKey(tbl_district, on_delete=models.CASCADE)
    status = models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)

    def __str__(self):
        return self.place_name

class tbl_stationmaster(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    master_gender = models.CharField(max_length=20)
    master_contact = models.CharField(max_length=20)
    master_address = models.TextField()
    master_place = models.ForeignKey(tbl_place, on_delete=models.CASCADE)
    master_photo = models.FileField(upload_to='UserImages/')
    master_proof = models.FileField(upload_to='UserImages/')
    status = models.IntegerField(default=1)

    def get_status_display(self):
        return 'Active' if self.status == 1 else 'Inactive'


class tbl_eventtype(models.Model):
    STATUS_CHOICES = [
        (1, 'Active'),
        (0, 'Inactive'),
    ]

    event_type = models.CharField(max_length=20)
    event_rate=models.IntegerField()
    event_details=models.CharField(max_length=5000)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return self.event_type


class tbl_boat(models.Model):
    STATUS_CHOICES = [
        (1, 'Active'),
        (0, 'Inactive'),
    ]

    boat_name = models.CharField(max_length=20)
    boat_service = models.CharField(max_length=50,default='1')
    boat_deck = models.CharField(max_length=50,default='Single Deck')
    boat_capacity = models.IntegerField()
    boat_entrydate = models.DateField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)


