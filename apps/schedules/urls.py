from .views import ShiftList
from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_schedule),
    path('get-schedule/', views.get_schedule),
    path('shift/', views.create_shift),
    # path('get-shift/', views.get_shifts),
    # path('get-shift/', views.ShiftList.as_view()),
]


router = DefaultRouter()
router.register('get-shift', ShiftList, basename='get-shift')

urlpatterns += router.urls   # ✅ correct
