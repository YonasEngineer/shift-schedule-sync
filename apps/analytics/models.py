from django.db import models
from apps.core.models.base import BaseModel

# Create your models here.


class UserWeeklyStats(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="weekly_stats")
    week_start = models.DateTimeField()

    total_hours = models.FloatField()
    overtime_hours = models.FloatField()

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "week_start"], name="unique_user_week")
        ]
