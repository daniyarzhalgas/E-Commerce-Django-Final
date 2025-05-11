from .models import Product
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status


class CreateProductTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('product-create')  # имя должно совпадать с name в urls.py

    def test_create_product(self):
        response = self.client.post(self.url)

        # Проверка кода ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка структуры созданного объекта
        self.assertIn('_id', response.data)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['name'].strip(), 'Product Name')
        self.assertEqual(response.data['brand'].strip(), 'Sample brand')
        self.assertEqual(response.data['category'].strip(), 'Sample category')


class ProductListTest(APITestCase):

    def setUp(self):
        # Optionally create a user and some products
        self.user = User.objects.create_user(username='testuser', password='testpass')

        Product.objects.create(
            user=self.user,
            name="Test Product",
            brand="Test Brand",
            category="Test Category",
            description="Test Description",
            price=100.0,
            countInStock=10
        )

    def test_get_products_list(self):
        url = reverse('products')  # name="products" from your urls
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('products', response.data)
        self.assertIn('page', response.data)
        self.assertIn('pages', response.data)

        self.assertGreaterEqual(len(response.data['products']), 1)

        product = response.data['products'][0]
        self.assertIn('name', product)
        self.assertIn('description', product)
        self.assertIn('price', product)


class SingleProductTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(
            user=self.user,
            name="Test Product",
            brand="Test Brand",
            category="Test Category",
            description="Test Description",
            price=100.0,
            countInStock=10
        )

    def test_get_single_product(self):
        url = reverse('product', args=[self.product._id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['_id'], self.product._id)
        self.assertEqual(response.data['name'], self.product.name)
        self.assertEqual(float(response.data['price']), float(self.product.price))
        self.assertIn('description', response.data)
        self.assertIn('countInStock', response.data)


class CreateProductTest(APITestCase):

    def setUp(self):
        # Creating an admin user instead of a regular user
        self.user = User.objects.create_superuser(username='adminuser', password='adminpass')
        self.client = APIClient()

        # Log in as the admin user to get the auth token
        response = self.client.post('/api/token/', {'username': 'adminuser', 'password': 'adminpass'})
        self.token = response.data['access']  # Get the access token

        # Set the Authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.url = reverse('create_product')  # Ensure this matches the name in your urls.py

    def test_create_product(self):
        # Send POST request to create a product
        response = self.client.post(self.url, data={})

        # Assert that the request was successful (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the returned data contains the expected product details
        self.assertIn('_id', response.data)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['name'].strip(), 'Product Name')
        self.assertEqual(response.data['brand'].strip(), 'Sample brand')
        self.assertEqual(response.data['category'].strip(), 'Sample category')

    def test_create_product_non_admin(self):
        # Test case where a non-admin user tries to create a product
        non_admin_user = User.objects.create_user(username='nonadminuser', password='nonadminpass')
        response = self.client.post('/api/token/', {'username': 'nonadminuser', 'password': 'nonadminpass'})
        non_admin_token = response.data['access']  # Get the token for non-admin user

        # Set the Authorization header with the non-admin token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_admin_token}')

        response = self.client.post(self.url, data={})

        # Assert that non-admin users cannot create products
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class ProductDeleteTest(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpass')
        self.client = APIClient()

        # Log in as admin to get the token
        response = self.client.post('/api/token/', {'username': 'adminuser', 'password': 'adminpass'})
        self.token = response.data['access']  # Get the token for admin

        # Set the Authorization header for the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create a product to delete
        self.product = Product.objects.create(
            name="Test Product",
            price="100.00",
            countInStock=10,
            user=self.admin_user
        )

        # URL for deleting the product
        self.url = reverse('delete_product', kwargs={'pk': self.product._id})  # Make sure the reverse URL name matches

    def test_delete_product(self):
        # Send the DELETE request
        response = self.client.delete(self.url)

        # Assert that the status code is 200 (success)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the success message
        self.assertEqual(response.data, "Product deleted successfully")

        # Check that the product has been deleted from the database
        with self.assertRaises(Product.DoesNotExist):
            # Use _id instead of id
            Product.objects.get(_id=self.product._id)

    def test_delete_product_non_admin(self):
        # Create a non-admin user
        non_admin_user = User.objects.create_user(username='nonadminuser', password='nonadminpass')

        # Log in as the non-admin user to get the token
        response = self.client.post('/api/token/', {'username': 'nonadminuser', 'password': 'nonadminpass'})
        non_admin_token = response.data['access']  # Get the token for the non-admin user

        # Set the Authorization header for the non-admin client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_admin_token}')

        # Send the DELETE request as a non-admin
        response = self.client.delete(self.url)

        # Assert that the status code is 403 (Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check that the product was not deleted
        self.assertTrue(Product.objects.filter(_id=self.product._id).exists())


class UserLoginTest(APITestCase):

    def setUp(self):
        # Create test user
        self.admin_user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True,  # or is_superuser=True if needed
        )
        self.login_url = reverse('login')  # make sure your `urls.py` names it as `login`

    def test_login_success(self):
        data = {
            "username": "admin@sdu.kz",
            "password": "admin"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], "admin@sdu.kz")
        self.assertTrue(response.data['isAdmin'])

    def test_login_invalid_credentials(self):
        data = {
            "username": "admin@sdu.kz",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_missing_fields(self):
        data = {
            "username": "",
            "password": ""
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

