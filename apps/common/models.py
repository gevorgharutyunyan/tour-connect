from django.db import models
from django_countries.fields import CountryField

class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    country = CountryField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    def __str__(self):
        return f"{self.name}, {self.country.name}"