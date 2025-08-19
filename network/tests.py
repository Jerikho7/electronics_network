from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.test import RequestFactory
from users.models import User
from network.models import NetworkNode, Product
from network.serializers import NetworkNodeSerializer, ProductSerializer
from network.permissions import IsActiveStaff
from network.admin import NetworkNodeAdmin


# --- MODEL TESTS ---
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

    def test_node_creation_and_levels(self):
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.retailer.level, 1)

    def test_supplier_cycle_validation(self):
        with self.assertRaises(ValidationError):
            self.factory.supplier = self.retailer
            self.factory.save()

    def test_direct_cycle_validation(self):
        node = NetworkNode.objects.create(
            name="Loop",
            email="loop@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="1"
        )
        node.supplier = node
        with self.assertRaises(ValidationError):
            node.save()

    def test_max_hierarchy_level(self):
        factory = self.factory
        retailer = self.retailer
        ip = NetworkNode.objects.create(
            name="IP",
            email="ip@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="3",
            supplier=retailer  # уровень 2
        )
        with self.assertRaises(ValidationError):
            NetworkNode.objects.create(
                name="Invalid",
                email="inv@test.com",
                country="Test",
                city="Test",
                street="Test",
                house_number="4",
                supplier=ip  # должно упасть (уровень 3)
            )

    def test_str_network_node(self):
        self.assertIn("Test Factory", str(self.factory))


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

    def test_product_creation_and_str(self):
        self.assertEqual(self.product.owner.name, "Test Node")
        self.assertEqual(str(self.product), "Test Product Model X")


# --- SERIALIZER TESTS ---
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

    def test_product_serializer_create(self):
        serializer = ProductSerializer(data=self.product_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
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

    def test_node_serializer_create(self):
        serializer = NetworkNodeSerializer(data=self.node_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        node = serializer.save()
        self.assertEqual(node.name, "Test Retailer")
        self.assertEqual(serializer.data["level"], 1)

    def test_update_node_does_not_change_debt(self):
        node = NetworkNode.objects.create(
            name="Retailer",
            email="r@test.com",
            country="Test",
            city="Test",
            street="Test",
            house_number="9",
            supplier=self.factory,
            debt=500
        )
        serializer = NetworkNodeSerializer(node, data={"debt": 0}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.debt, 500)  # debt не изменился


# --- VIEWSET TESTS ---
class NetworkNodeViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.ru",
            password="testpass123",
            is_staff=True
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

    def test_filter_by_country(self):
        response = self.client.get("/api/nodes/?country=Test Country")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@mail.ru",
            password="testpass123",
            is_staff=True
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


# --- PERMISSION TESTS ---
class PermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsActiveStaff()

    def test_active_staff_has_permission(self):
        user = User.objects.create_user(email="staff@test.com", password="123", is_staff=True, is_active=True)
        request = self.factory.get("/api/nodes/")
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_inactive_user_has_no_permission(self):
        user = User.objects.create_user(email="inactive@test.com", password="123", is_staff=False, is_active=False)
        request = self.factory.get("/api/nodes/")
        request.user = user
        self.assertFalse(self.permission.has_permission(request, None))


# --- ADMIN ACTION TEST ---
class AdminActionTest(TestCase):
    def setUp(self):
        self.node = NetworkNode.objects.create(
            name="Factory",
            email="f@test.com",
            country="X",
            city="Y",
            street="Street",
            house_number="1",
            debt=100
        )
        self.admin = NetworkNodeAdmin(NetworkNode, AdminSite())
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = User.objects.create_superuser(
            email="admin@test.com",
            password="12345"
        )

        setattr(self.request, "session", self.client.session)
        messages = FallbackStorage(self.request)
        setattr(self.request, "_messages", messages)

    def test_clear_debt_action(self):
        queryset = NetworkNode.objects.filter(id=self.node.id)
        self.admin.clear_debt(self.request, queryset)
        self.node.refresh_from_db()
        self.assertEqual(float(self.node.debt), 0.0)
