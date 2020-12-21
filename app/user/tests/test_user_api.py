from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """
    Test the users API (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test Creating user with valid payload successful
        """
        payload = {
            'email': 'test@test.com',
            'password': 'test@123',
            'name': 'Testy'
        }

        response = self.client.post(CREATE_USER_URL, payload)
        # Test user created through status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test created user
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exist(self):
        """
        Test Create a user that already exist fails
        """
        payload = {
            'email': 'test@test.com',
            'password': 'test@123'
        }

        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test that the password must be more than 5 chars
        """
        payload = {
            'email': 'test@test.com',
            'password': 'test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test that a token is created for user
        """
        payload = {
            'email': 'test@test.com',
            'password': 'test2123'
        }

        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that a token is not created for user
        if invalid credentials are given
        """
        create_user(email='test@test.com', password='test2123')

        # Password in payload is different from that in user created
        payload = {
            'email': 'test@test.com',
            'password': 'test@123'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not creaated if userdoes not exist
        :return:
        """
        payload = {
            'email': 'test@test.com',
            'password': 'test@123'
        }

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test That email and password are required
        :return:
        """
        response = self.client.post(
            TOKEN_URL,
            {'email': 'one', 'password': ''}
        )
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorizd(self):
        """
        Test that authentication is required for users
        :return:
        """
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """
    Test Api Requests that require authentication
    """

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='test@123',
            name='Mohammad'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in user
        :return:
        """
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {
                'email': self.user.email,
                'name': self.user.name
            }
        )

    def test_post_me_not_allowed(self):
        """
        TEst that post is not allowed on the ME URL
        :return:
        """
        response = self.client.post(ME_URL, {})
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """TEst updating user profile for authenticated user"""
        payload = {
            'name': 'my name',
            'password': 'test@123'
        }

        response = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
