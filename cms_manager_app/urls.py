from django.urls import path
from . import views

urlpatterns = [
    path("manager-index/", views.manager_index, name="manager-index"),
    path('get-today-order',views.TodaysOrdersView.as_view(),name="get-today-order"),
    path("add-new-table/", views.add_table, name="add-table"),
    path("edit-table/", views.edit_table, name="edit-table"),
    path("update-table/<int:table_id>", views.update_table, name="update-table"),
    path("add-new-dish/", views.add_dish, name="add-dish"),
    path("edit-dish/", views.edit_dish, name="edit-dish"),
    path("update-dish/<int:dish_id>", views.update_dish, name="update-dish"),
    path("print-preview/", views.print_preview, name="print-preview"),
]
