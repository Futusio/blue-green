from django.db import models


class Order(models.Model):
    title = models.CharField(max_length=100)
    is_fixed = models.BooleanField(default=True)
    profile_id = models.IntegerField(default=1)
    new_table = models.IntegerField(null=True)
    some_migrate = models.BooleanField(default=False)

