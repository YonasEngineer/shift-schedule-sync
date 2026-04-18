from django.urls import path

from . import views

urlpatterns = [
    path("create-swap/",  views.create_swap),
    path("get-myswaps/", views.GetSwaps.as_view()),
    path("needing/approval/<uuid:location_id>/",
         views.get_needing_manager_approval),
    path("accept-swap/<uuid:swap_id>/", views.accept_swap),
    path("reject-swap/<uuid:swap_id>/", views.reject_swap),
    path("approve/",  views.manager_approve),
    path("reject/", views.manager_reject)
]
