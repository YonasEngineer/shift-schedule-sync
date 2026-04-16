from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', views.login_view),
    path('auth/get-csrf/', views.get_csrf_token),
    path('get-skill/', views.get_user_skill),
    path('get-available-staff/', views.get_available_staff),




]
