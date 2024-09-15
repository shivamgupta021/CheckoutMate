from django.urls import reverse

from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status

from accounts.models import User
from products.models import Product
from products.views import ProductViewSet
from products.serializers import ProductSerializer


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.product = Product.objects.create(
            name="Product", description="Description", price=100, quantity=10
        )
        self.employee = User.objects.create_user(
            name="employee",
            password="employeepassword",
            email="employee@gmail.com",
            role="EMPLOYEE",
            age=38,
        )
        self.customer = User.objects.create_user(
            name="customer",
            password="customerpassword",
            email="customer@gmail.com",
            role="CUSTOMER",
            age=28,
        )
        self.view = ProductViewSet.as_view({"get": "list", "post": "create"})

    def test_get_product_list(self):
        """Anyone can access the products list"""
        request = self.factory.get(reverse("product-list"))
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_product(self):
        view = ProductViewSet.as_view({"get": "retrieve"})
        request = self.factory.get(
            reverse("product-detail", kwargs={"pk": self.product.pk})
        )
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Product")

    def test_create_product_employee(self):
        """Only employees can create a product"""
        data = {
            "name": "New Product",
            "description": "This is a new product",
            "price": 15.00,
            "quantity": 50,
        }
        request = self.factory.post(reverse("product-list"), data)
        force_authenticate(request, user=self.employee)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_customer(self):
        """Customers cannot create a product"""
        data = {
            "name": "New Product",
            "description": "This is a new product",
            "price": 15.00,
            "quantity": 50,
        }
        request = self.factory.post(reverse("product-list"), data)
        force_authenticate(request, user=self.customer)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_update_product_employee(self):
        view = ProductViewSet.as_view({"put": "update"})
        data = {
            "name": "Updated Product",
            "description": "This is an updated product",
            "price": 20.00,
            "quantity": 75,
        }
        request = self.factory.put(
            reverse("product-detail", kwargs={"pk": self.product.pk}), data
        )
        force_authenticate(request, user=self.employee)
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")

    def test_update_product_customer(self):
        view = ProductViewSet.as_view({"put": "update"})
        data = {
            "name": "Updated Product",
            "description": "This is an updated product",
            "price": 20.00,
            "quantity": 75,
        }
        request = self.factory.put(
            reverse("product-detail", kwargs={"pk": self.product.pk}), data
        )
        force_authenticate(request, user=self.customer)
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        self.assertNotEqual(self.product.name, "Updated Product")

    def test_delete_product_employee(self):
        view = ProductViewSet.as_view({"delete": "destroy"})
        request = self.factory.delete(
            reverse("product-detail", kwargs={"pk": self.product.pk})
        )
        force_authenticate(request, user=self.employee)
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_customer(self):
        view = ProductViewSet.as_view({"delete": "destroy"})
        request = self.factory.delete(
            reverse("product-detail", kwargs={"pk": self.product.pk})
        )
        force_authenticate(request, user=self.customer)
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)
