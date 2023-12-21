from django.db import models


class Upgrade(models.Model):
    title = models.CharField(max_length=100)
    is_fixed = models.BooleanField(default=True)
    profile_code = models.IntegerField(default=1)
    new_table = models.IntegerField(null=True)

    second_migrate = models.IntegerField(default=0)
    # copy_field = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["profile_code"]),
        ]


class SubtitleNCorModel(models.Model):
    title = models.CharField(max_length=12)


class WoWModel(models.Model):
    title = models.CharField(max_length=12)