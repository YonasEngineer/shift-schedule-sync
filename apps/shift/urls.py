from . import views
from django.urls import path
urlpatterns = [
    path('shift/', views.create_shift, name="create-shift"),
    path('login/', views.login_view, name="login")
]
