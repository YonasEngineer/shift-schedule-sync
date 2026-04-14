from django.db import models
from apps.core.models.base import BaseModel
# Create your models here.


class SwapManagerStatus(models.TextChoices):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SwapRequestType(models.TextChoices):
    SWAP = "SWAP"
    DROP = "DROP"


class SwapRequestStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class SwapRequest(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shift = models.ForeignKey(
        "schedules.Shift", on_delete=models.CASCADE, related_name="swap_requests")

    requester = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="requested_swaps")
    target_user = models.ForeignKey(
        "users.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="targeted_swaps")

    type = models.CharField(max_length=10, choices=SwapRequestType.choices)

    status = models.CharField(
        max_length=20, choices=SwapRequestStatus.choices, default=SwapRequestStatus.PENDING)
    manager_status = models.CharField(
        max_length=20, choices=SwapManagerStatus.choices, default=SwapManagerStatus.PENDING)

    expires_at = models.DateTimeField(null=True, blank=True)

    processed_by = models.ForeignKey(
        "users.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_swaps")
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "swap_requests"
        indexes = [
            models.Index(fields=["status", "expires_at"])
        ]
