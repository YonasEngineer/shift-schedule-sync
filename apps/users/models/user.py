from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models.base import BaseModel


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    VENDOR = 'vendor', 'Vendor'
    CUSTOMER = 'customer', 'Customer'


class CustomUser(AbstractUser, BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    # is_active = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    skills = models.ManyToManyField(
        "Skill",
        through='UserSkill',  # Here model name
        related_name='users'
    )
    locations = models.ManyToManyField(
        'locations.Location', through='locations.UserLocation', related_name='users')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True,)
    # This controls which columns appear in the table list

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"


class UserPreference(BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="preferences")
    desired_hours_per_week = models.IntegerField()

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"
