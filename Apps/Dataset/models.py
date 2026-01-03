from django.conf import settings
from django.db import models


class Dataset(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="datasets",
    )
    name = models.CharField(max_length=120)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    last_order_number = models.PositiveIntegerField(default=100)
    last_inventory_item_number = models.PositiveIntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class InventoryItem(models.Model):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="inventory_items",
    )
    item_id = models.CharField(max_length=20)
    item_name = models.CharField(max_length=120)
    item_category = models.CharField(max_length=80)
    barcode_number = models.CharField(max_length=80, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["dataset", "item_id"],
                name="unique_item_id_per_dataset",
            )
        ]

    def __str__(self):
        return f"{self.item_id} - {self.item_name}"
