from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User

from .serializers import NetworkNodeSerializer, ProductSerializer

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import NetworkNode, Product

User = get_user_model()

class NetworkNodeModelTest(TestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Test Factory",
            email="factory@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )
        self.retailer = NetworkNode.objects.create(
            name="Test Retailer",
            email="retailer@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="456",
            supplier=self.factory
        )

    def test_node_creation(self):
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.retailer.level, 1)

    def test_supplier_cycle_validation(self):
        with self.assertRaises(ValidationError):
            self.factory.supplier = self.retailer
            self.factory.save()

    def test_max_hierarchy_level(self):
        """Проверяем, что нельзя создать 4-й уровень иерархии."""
        # Создаем цепочку: factory -> retailer -> ip
        factory = NetworkNode.objects.create(
            name="Factory",
            email="f@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="1"
        )

        retailer = NetworkNode.objects.create(
            name="Retailer",
            email="r@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="2",
            supplier=factory  # Уровень 1
        )

        ip = NetworkNode.objects.create(
            name="IP",
            email="ip@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="3",
            supplier=retailer  # Уровень 2
        )

        # Пытаемся создать 4-й уровень
        with self.assertRaises(ValidationError):
            NetworkNode.objects.create(
                name="Invalid",
                email="inv@test.com",
                country="Test",
                city="Test",
                street="Test",
                house_number="4",
                supplier=ip  # Должно вызвать ошибку (уровень 3)
            )

class ProductModelTest(TestCase):
    def setUp(self):
        self.node = NetworkNode.objects.create(
            name="Test Node",
            email="node@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )
        self.product = Product.objects.create(
            owner=self.node,
            title="Test Product",
            model="Model X",
            release_date="2023-01-01"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.owner.name, "Test Node")
        self.assertEqual(str(self.product), "Test Product Model X")


class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.node = NetworkNode.objects.create(
            name="Test Node",
            email="node@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )
        self.product_data = {
            "owner": self.node.id,
            "title": "Test Product",
            "model": "Model X",
            "release_date": "2023-01-01"
        }

    def test_product_serializer(self):
        serializer = ProductSerializer(data=self.product_data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.title, "Test Product")
        self.assertEqual(serializer.data["owner_name"], "Test Node")


class NetworkNodeSerializerTest(APITestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Test Factory",
            email="factory@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )
        self.node_data = {
            "name": "Test Retailer",
            "email": "retailer@test.com",
            "country": "Test Country",
            "city": "Test City",
            "street": "Test Street",
            "house_number": "456",
            "supplier": self.factory.id
        }

    def test_node_serializer(self):
        serializer = NetworkNodeSerializer(data=self.node_data)
        self.assertTrue(serializer.is_valid())
        node = serializer.save()
        self.assertEqual(node.name, "Test Retailer")
        self.assertEqual(serializer.data["level"], 1)

class NetworkNodeViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.ru",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.factory = NetworkNode.objects.create(
            name="Test Factory",
            email="factory@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )

    def test_list_nodes(self):
        response = self.client.get("/api/nodes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_node(self):
        data = {
            "name": "New Node",
            "email": "new@test.com",
            "country": "Test Country",
            "city": "Test City",
            "street": "Test Street",
            "house_number": "456",
            "supplier": self.factory.id
        }
        response = self.client.post("/api/nodes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkNode.objects.count(), 2)


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.ru",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.node = NetworkNode.objects.create(
            name="Test Node",
            email="node@test.com",
            country="Test Country",
            city="Test City",
            street="Test Street",
            house_number="123"
        )

    def test_create_product(self):
        data = {
            "owner": self.node.id,
            "title": "New Product",
            "model": "Model Y",
            "release_date": "2023-01-01"
        }
        response = self.client.post("/api/products/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
