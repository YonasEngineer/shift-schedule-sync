from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# ROLE_CHOICES = (
#     ('admin', 'Admin'),
#     ('manager', 'manager'),
#     ('staff', 'staff'),
# )


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    VENDOR = 'vendor', 'Vendor'
    CUSTOMER = 'customer', 'Customer'


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True,)
