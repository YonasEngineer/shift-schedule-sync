from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.
# admin.site.register(CustomUser)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # THIS is where list_display belongs
    list_display = ('email', 'username', 'phone_number', 'role', 'is_staff')
