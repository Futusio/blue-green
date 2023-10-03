from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)


class Address(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=2048)
    city = models.IntegerField(default=1)
