from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """
    Test the publicly available ingredients API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test Ingredients List login required
        """
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test@123'
        )
        self.client.force_authenticate(self.user)

    def test_create_ingredient_successful(self):
        """
        Test Create successfully a new ingredient
        """
        payload = {
            'name': 'Salt'
        }
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """
        Test create a new ingredient with invalid data
        :return:
        """
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_list_for_authenticated_user(self):
        """
        Retrieves list of ingredients for authenticated user
        """

        Ingredient.objects.create(name='Salt', user=self.user)
        Ingredient.objects.create(name='Lettuce', user=self.user)
        Ingredient.objects.create(name='Lemon', user=self.user)

        ingredients = Ingredient.objects \
            .all() \
            .order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
        Test that ingredients for the authenticated user only are returned
        """

        user2 = get_user_model().objects.create_user(
            email='test2@email.com',
            password='password'
        )

        Ingredient.objects.create(name='Salt', user=user2)

        ingredient = Ingredient.objects.create(user=self.user, name='Tomato')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
