from django.urls import path
from . import views

__project_by__ = "RajeshKumar"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("registration/", views.user_registration, name="register"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        views.reset_confirm,
        name="passwordresetconfirm",
    ),
    path("user-detail/", views.staff_details, name="user-detail"),
    path("edit-user-detail/<int:staff_id>", views.edit_staff_detail, name="edit-user-detail"),
]
