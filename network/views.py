from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer
from .filters import NetworkNodeFilter


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    API для управления узлами сети (NetworkNode).

    Доступные действия:
        - GET /api/nodes/ — список узлов (с фильтрацией и поиском).
        - GET /api/nodes/{id}/ — детальная информация об узле.
        - POST /api/nodes/ — создание нового узла.
        - PATCH /api/nodes/{id}/ — частичное обновление (поле debt игнорируется).
        - DELETE /api/nodes/{id}/ — удаление узла.

    Особенности:
        - Доступ только для аутентифицированных пользователей.
        - Фильтрация по стране через DjangoFilterBackend.
        - Поиск по имени, городу, стране, email.
        - Сортировка по имени, городу, стране, дате создания.
    """

    queryset = NetworkNode.objects.select_related("supplier").prefetch_related("products")
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NetworkNodeFilter
    search_fields = ["name", "city", "country", "email"]
    ordering_fields = ["name", "city", "country", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    """
    API для управления продуктами (Product).

    Доступные действия:
        - GET /api/products/ — список продуктов.
        - GET /api/products/{id}/ — детальная информация о продукте.
        - POST /api/products/ — создание нового продукта.
        - PATCH /api/products/{id}/ — частичное обновление.
        - DELETE /api/products/{id}/ — удаление продукта.

    Особенности:
        - Доступ только для аутентифицированных пользователей.
        - Поиск по названию, модели и имени владельца.
        - Сортировка по дате выхода и названию.
    """

    queryset = Product.objects.select_related("owner")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "model", "owner__name", "owner__city"]
    ordering_fields = ["release_date", "title"]
