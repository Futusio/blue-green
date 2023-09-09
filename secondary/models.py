from django.db import models


class Order(models.Model):
    title = models.CharField(max_length=100)
    is_fixed = models.BooleanField(default=True)
    profile_id = models.IntegerField(null=True)

