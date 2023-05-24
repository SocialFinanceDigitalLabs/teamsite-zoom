from django.contrib.auth.models import User
from django.db import models


class OauthToken(models.Model):
    service = models.CharField(max_length=20, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires = models.DateTimeField()

    def __str__(self):
        return f"{self.service} expires {self.expires})"


class ZoomProfile(models.Model):
    zoom_id = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, editable=False, related_name="zoom_profile"
    )
    dept = models.CharField(max_length=100, blank=True, null=True, default=None)
    pic_url = models.CharField(max_length=255, blank=True, null=True, default=None)
    phone_number = models.CharField(max_length=50, blank=True, null=True, default=None)
    extension_number = models.IntegerField(null=True, blank=True, default=None)
    presence_status = models.CharField(
        max_length=50, blank=True, null=True, default=None
    )
    presence_status_updated = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.user.username} [{self.zoom_id}] ext {self.extension_number}"


class CallingPlan(models.Model):
    zoom_profile = models.ForeignKey(
        ZoomProfile, on_delete=models.CASCADE, related_name="calling_plans"
    )
    type = models.IntegerField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.zoom_profile.user.username} {self.type} {self.name}"


class AssignedNumber(models.Model):
    zoom_profile = models.ForeignKey(
        ZoomProfile, on_delete=models.CASCADE, related_name="assigned_numbers"
    )
    number = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.zoom_profile.user.username} {self.number} {self.location}"
