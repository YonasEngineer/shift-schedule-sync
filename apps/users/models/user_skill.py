from django.db import models
import uuid
from apps.core.models.base import BaseModel


class UserSkill(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "CustomUser",   # ✅ string reference (important)
        on_delete=models.CASCADE,
        related_name="user_skills"
    )

    skill = models.ForeignKey(
        "Skill",  # here we can use "users.Skill" or  "Skill"
        on_delete=models.CASCADE,
        related_name="user_skills"
    )
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_skills"
