from django.db import models
from apps.core.models.base import BaseModel

# Create your models here.


class AuditAction(models.TextChoices):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class EntityType(models.TextChoices):
    SHIFT = "SHIFT"
    ASSIGNMENT = "ASSIGNMENT"
    SWAP = "SWAP"


class AuditLog(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    entity_id = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=AuditAction.choices)

    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)

    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="audit_logs")

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["user", "created_at"]),
        ]
