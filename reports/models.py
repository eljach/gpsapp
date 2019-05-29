import datetime
from django.db import models
from address.models import AddressField


class Employee(models.Model):
    name = models.CharField(max_length=20)
    name_id = models.CharField(max_length=30, unique=True, blank=True, null=True)

class Building(models.Model):
    building_identifier = models.CharField(max_length=30, unique=True, blank=True, null=True)
    street_number = models.CharField(max_length=20, blank=True)
    route = models.CharField(max_length=100, blank=True)
    locality = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def get_location(self):
        return (self.latitude, self.longitude)


class Visit(models.Model):
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name="visits", null=True)
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    time_on_site = models.DateTimeField()

    def get_time_since_last_visit(self):
        return  datetime.datetime.today() - self.departure_time

    def save(self, *args, **kwargs):
        if not self.pk:
            self.time_on_site = self.departure_time - self.arrival_time
        super(Visit, self).save(*args, **kwargs)

class Position(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="positions", null=True)
    date = models.DateTimeField()
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    accuracy = models.IntegerField()
    already_analyzed = models.BooleanField(default=False)

    def get_location(self):
        return (self.lat, self.lng)
