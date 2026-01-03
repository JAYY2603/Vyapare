from django.urls import path

from . import views

app_name = "dataset"

urlpatterns = [
    path("datasets/", views.dataset_list, name="dataset_list"),
    path("datasets/api/create/", views.api_create_dataset,
         name="api_create_dataset"),
    path(
        "datasets/<int:dataset_id>/sales/init/",
        views.api_init_sale,
        name="api_init_sale",
    ),
    path(
        "datasets/<int:dataset_id>/sales/record/",
        views.api_record_sale,
        name="api_record_sale",
    ),
    path(
        "datasets/<int:dataset_id>/inventory/init/",
        views.api_init_inventory,
        name="api_init_inventory",
    ),
    path(
        "datasets/<int:dataset_id>/inventory/create/",
        views.api_create_inventory,
        name="api_create_inventory",
    ),
    path(
        "datasets/<int:dataset_id>/inventory/list/",
        views.api_list_inventory,
        name="api_list_inventory",
    ),
    path(
        "datasets/<int:dataset_id>/inventory/<int:inventory_id>/update/",
        views.api_update_inventory,
        name="api_update_inventory",
    ),
    path(
        "datasets/<int:dataset_id>/export/",
        views.export_dataset_excel,
        name="export_dataset_excel",
    ),
]
