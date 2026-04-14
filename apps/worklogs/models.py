from django.db import models
from apps.core.models.base import BaseModel
# Create your models here.


class WorkLog(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="work_logs")
    shift = models.ForeignKey(
        "schedules.Shift", on_delete=models.CASCADE, related_name="work_logs")

    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_logs"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "shift"], name="unique_worklog")
        ]
