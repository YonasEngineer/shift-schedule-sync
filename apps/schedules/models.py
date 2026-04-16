from django.db import models
import uuid
from apps.core.models.base import BaseModel
# Create your models here.


class ScheduleStatus(models.TextChoices):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ShiftStatus(models.TextChoices):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class AssignmentStatus(models.TextChoices):
    ASSIGNED = "ASSIGNED"
    PENDING_SWAP = "PENDING_SWAP"
    PENDING_DROPPED = "PENDING_DROPPED"
    COMPLETED_SWAP = "COMPLETED_SWAP"
    COMPLETED_DROPPED = "COMPLETED_DROPPED"


class Schedule(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(
        "locations.Location",   # ✅ add app name
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    creator = models.ForeignKey(
        "users.CustomUser",     # ✅ correct user model + app name
        on_delete=models.CASCADE,
        related_name="created_schedules"
    )
    week_start = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=ScheduleStatus.choices, default=ScheduleStatus.DRAFT)
    publish_cutoff_hours = models.IntegerField(default=48)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)


class Shift(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    location = models.ForeignKey(
        "locations.Location", on_delete=models.CASCADE, related_name="shifts")
    schedule = models.ForeignKey(
        Schedule, on_delete=models.SET_NULL, null=True, related_name="shifts")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    required_skill = models.ForeignKey(
        "users.Skill", on_delete=models.CASCADE, related_name="shifts")
    required_headcount = models.IntegerField()

    creator = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="created_shifts")

    status = models.CharField(
        max_length=20, choices=ShiftStatus.choices, default=ShiftStatus.DRAFT)
    is_premium = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shifts"
        indexes = [
            models.Index(fields=["location", "start_time"])
        ]


class ShiftAssignment(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE, related_name="assignments")
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="shift_assignments")

    status = models.CharField(
        max_length=30, choices=AssignmentStatus.choices, default=AssignmentStatus.ASSIGNED)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shift_assignments"
        constraints = [
            models.UniqueConstraint(
                fields=["shift", "user"], name="unique_shift_user")
        ]
        indexes = [
            models.Index(fields=["user", "status"])
        ]
