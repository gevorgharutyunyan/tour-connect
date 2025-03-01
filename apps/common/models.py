from django.db import models
from django_countries.fields import CountryField

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=2, unique=True, null=True, blank=True)  # ISO 639-1 language code

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    country = CountryField()

    def __str__(self):
        return f"{self.name}, {self.country.name}"