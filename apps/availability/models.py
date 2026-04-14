from django.db import models
from apps.core.models.base import BaseModel
import uuid
# Create your models here.


class AvailabilityRecurring(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="recurring_availabilities")

    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    timezone = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "availability_recurring"


class AvailabilityException(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="availability_exceptions")

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "availability_exception"
        indexes = [
            models.Index(fields=["user", "date"])
        ]
