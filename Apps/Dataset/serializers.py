from rest_framework import serializers

from .models import Dataset, InventoryItem


class CreateDatasetSerializer(serializers.Serializer):
    dataset_name = serializers.CharField(max_length=120)

    def validate_dataset_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Dataset name is required.")

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if Dataset.objects.filter(
                user=request.user,
                name__iexact=cleaned,
            ).exists():
                raise serializers.ValidationError(
                    "A dataset with this name already exists."
                )

        return cleaned


class CreateDatasetResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    dataset_id = serializers.IntegerField()
    dataset_name = serializers.CharField()
    created_at = serializers.DateTimeField()


class SaleItemSerializer(serializers.Serializer):
    item = serializers.CharField(max_length=120)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0)
    category = serializers.CharField(max_length=80)

    def validate_item(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Item name is required.")
        return cleaned

    def validate_category(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Category is required.")
        return cleaned


class RecordSaleSerializer(serializers.Serializer):
    items = SaleItemSerializer(many=True, min_length=1)
    payment_type = serializers.CharField(max_length=50)

    def validate_payment_type(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Payment type is required.")
        return cleaned


class RecordSaleResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    order_id = serializers.CharField()
    item_count = serializers.IntegerField()
    recorded_at = serializers.CharField()


class InitSaleResponseSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    current_datetime = serializers.CharField()


class InitInventoryResponseSerializer(serializers.Serializer):
    item_id = serializers.CharField()


class CreateInventoryItemSerializer(serializers.Serializer):
    item_id = serializers.CharField(max_length=20)
    item_name = serializers.CharField(max_length=120)
    item_category = serializers.CharField(max_length=80)
    barcode_number = serializers.CharField(
        max_length=80, required=False, allow_blank=True)
    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0)
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0)

    def validate_item_id(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("ItemID is required.")
        return cleaned

    def validate_item_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("ItemName is required.")
        return cleaned

    def validate_item_category(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("ItemCategory is required.")
        return cleaned

    def validate(self, attrs):
        request = self.context.get("request")
        dataset = self.context.get("dataset")

        if request and dataset:
            if dataset.user_id != request.user.id:
                raise serializers.ValidationError("Dataset not found.")

            if InventoryItem.objects.filter(
                dataset=dataset,
                item_id=attrs["item_id"],
            ).exists():
                raise serializers.ValidationError(
                    {"item_id": "This ItemID already exists in this dataset."}
                )

            barcode = attrs.get("barcode_number", "").strip()
            if barcode and InventoryItem.objects.filter(
                dataset=dataset,
                barcode_number=barcode,
            ).exists():
                raise serializers.ValidationError(
                    {"barcode_number": "This barcode already exists in this dataset."}
                )

        attrs["barcode_number"] = attrs.get("barcode_number", "").strip()
        return attrs


class CreateInventoryItemResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    item_id = serializers.CharField()
    item_name = serializers.CharField()


class InventoryListItemSerializer(serializers.Serializer):
    inventory_id = serializers.IntegerField()
    item_id = serializers.CharField()
    item_name = serializers.CharField()
    item_category = serializers.CharField()
    barcode_number = serializers.CharField(allow_blank=True)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.CharField()


class InventoryListResponseSerializer(serializers.Serializer):
    items = InventoryListItemSerializer(many=True)


class UpdateInventoryItemSerializer(serializers.Serializer):
    item_name = serializers.CharField(max_length=120)
    item_category = serializers.CharField(max_length=80)
    barcode_number = serializers.CharField(
        max_length=80, required=False, allow_blank=True)
    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0)
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0)

    def validate_item_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("ItemName is required.")
        return cleaned

    def validate_item_category(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("ItemCategory is required.")
        return cleaned

    def validate(self, attrs):
        dataset = self.context.get("dataset")
        inventory_item = self.context.get("inventory_item")

        if dataset and inventory_item:
            barcode = attrs.get("barcode_number", "").strip()
            if barcode and InventoryItem.objects.filter(
                dataset=dataset,
                barcode_number=barcode,
            ).exclude(id=inventory_item.id).exists():
                raise serializers.ValidationError(
                    {"barcode_number": "This barcode already exists in this dataset."}
                )

        attrs["barcode_number"] = attrs.get("barcode_number", "").strip()
        return attrs


class UpdateInventoryItemResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    inventory_id = serializers.IntegerField()
