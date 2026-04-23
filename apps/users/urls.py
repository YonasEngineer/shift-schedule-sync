from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    # TokenRefreshView,
)
urlpatterns = [
    path('auth/register/', views.register),
    # login  end point to get token or session
    path('auth/login/', views.login_view),
    # loged in end point to get JWT toekn
    # path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/get-csrf/', views.get_csrf_token),
    path('get-skill/', views.get_user_skill),
    path('get-available-staff/', views.get_available_staff),




]
