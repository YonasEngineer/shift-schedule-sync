from django.db import models
import uuid
from apps.core.models.base import BaseModel
# Create your models here.


class NotificationType(models.TextChoices):
    SHIFT_ASSIGNED = "SHIFT_ASSIGNED"
    SHIFT_REMINDER = "SHIFT_REMINDER"
    SWAP_REQUEST = "SWAP_REQUEST"
    SWAP_ACCEPTED = "SWAP_ACCEPTED"
    SWAP_REJECTED = "SWAP_REJECTED"
    GENERAL = "GENERAL"


class Notification(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="notifications")

    type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    is_read = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["user", "is_read"])
        ]
