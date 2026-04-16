from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_schedule),
    path('get-schedule/', views.get_schedule),
    path('shift/', views.create_shift),
    path('get-shift/', views.get_shifts),



]
