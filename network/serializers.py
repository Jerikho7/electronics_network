from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.

    Поля:
        id (int): Идентификатор продукта.
        owner (int): ID владельца (узла сети).
        owner_name (str): Название узла-владельца (только для чтения).
        title (str): Название продукта.
        model (str): Модель продукта.
        release_date (date): Дата выхода на рынок.
    """

    owner = serializers.PrimaryKeyRelatedField(queryset=NetworkNode.objects.all())
    owner_name = serializers.CharField(source="owner.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "owner", "owner_name", "title", "model", "release_date"]


class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели NetworkNode.

    Поля:
        id (int): Идентификатор узла.
        name (str): Название узла.
        email (str): Email контакта.
        country (str): Страна.
        city (str): Город.
        street (str): Улица.
        house_number (str): Номер дома.
        supplier (int): ID поставщика (узла сети).
        debt (decimal): Задолженность перед поставщиком.
        created_at (datetime): Дата создания.
        level (int): Уровень иерархии (0 — завод, 1 — розница, 2 — ИП).
        products (list[Product]): Продукты, принадлежащие узлу.
    """

    level = serializers.IntegerField(read_only=True)
    level_name = serializers.CharField(read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            "id", "name", "email", "country", "city", "street", "house_number",
            "supplier", "created_at", "debt", "level", "level_name", "products"
        ]

    read_only_fields = ("created_at",)

    def update(self, instance, validated_data):
        """
        Обновление узла сети.

        Поле "debt" защищено от изменения через API.
        """
        validated_data.pop("debt", None)
        return super().update(instance, validated_data)
