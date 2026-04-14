from django.db import models
from apps.core.models.base import BaseModel
import uuid
# from apps.users.models import CustomUser
# from ..users.models import CustomUser
# from django.db import models
# Create your models here.


class UserLocationRole(models.TextChoices):
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"


class Location(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "locations"

    def __str__(self):
        return f'{self.name} {(self.timezone)}'


class UserLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="user_locations")
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="location_users")
    role = models.CharField(max_length=20, choices=UserLocationRole.choices)
    is_certified = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_locations"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "location"], name="unique_user_location")
        ]
