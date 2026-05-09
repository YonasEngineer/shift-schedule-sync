from .views import ShiftList
from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
# from rest_framework.routers import SimpleRouter
urlpatterns = [
    # here we can use router,  if it defined above
    # path("",  include(router.urls)),
    path('', views.create_schedule),
    # path('get-schedule/', views.get_schedule),

    # path('get-schedule/', views.ScheduleViewSet.as_view()),
    path('shift/', views.create_shift),
    # path('get-shift/', views.get_shifts),
    # path('get-shift/', views.ShiftList.as_view()),
]


router = DefaultRouter()
router.register('get-shift', ShiftList, basename='get-shift')
router.register('get-schedule', views.ScheduleViewSet, basename='schedules')

urlpatterns += router.urls   # ✅ correct
