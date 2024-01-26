from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("temp-order/", views.temp_order, name="temp-order"),
    path("edit-temp-order/<int:order_id>/", views.edit_temp_order, name="edit-temp-order"),
    path("update-temp-order/<int:order_id>/", views.update_temp_order, name="update-temp-dish"),
    path("delete-temp-order/<int:order_id>/", views.delete_temp_order, name="delete-temp-order"),
    path("temp-order-list/", views.temp_order_list, name="temp-order-list"),
    path("order-list/", views.order_list, name="order-list"),
    path("display-order/<int:order_id>/", views.display_order, name="display-order"),
]
