from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


## user tests
class UserLoginTest(APITestCase):

    def setUp(self):
        # Create test user
        self.admin_user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True,
        )
        self.login_url = reverse('login')

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


class UserProfileTest(APITestCase):

    def setUp(self):
        # Create admin user
        self.user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True  # Mark as admin
        )
        # Get JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.profile_url = reverse('user_profile')

    def test_get_user_profile_authenticated(self):
        # Include Authorization header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@sdu.kz')
        self.assertTrue(response.data['isAdmin'])
        self.assertEqual(response.data['username'], 'admin@sdu.kz')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
