from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """
    Returns Recipe details URL
    :param recipe_id:
    :return: String
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Test Tag'):
    """
    Creates and returns a tag object
    :param user:
    :param name:
    :return: Tag
    """
    return Tag.objects.create(
        user=user,
        name=name,
    )


def sample_ingredient(user, name='Test Ingredient'):
    """
    Creates and returns a tag object
    :param user:
    :param name:
    :return: Ingredient
    """
    return Ingredient.objects.create(
        user=user,
        name=name,
    )


def sample_recipe(user, **params):
    """
    Creates and returns a simple recipe object
    :param user:
    :param params:
    :return: Recipe
    """
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00,
    }

    # Accepts dictionary object,
    # Updates all keys found in dictionary,
    # or create them if not exist
    defaults.update(params)

    return Recipe.objects.create(
        user=user,
        **defaults
    )


class PublicRecipeApiTest(TestCase):
    """
    Test the publicly available Recipe API
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """
    Test the private available Recipe API(Authenticated Users)
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test@123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_authenticated_user(self):
        """
        Test recieving recipes for authenticated user
        """
        user2 = get_user_model().objects.create_user(
            email='test2@gmail.com',
            password='test123'
        )

        sample_recipe(user=self.user)
        sample_recipe(user=user2)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(
            user=self.user
        )
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = recipe_detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
        Test creating recipe
        """
        payload = {
            'title': 'Choclate',
            'time_minutes': 30,
            'price': 32.25,
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        Test Create recipe with tag
        """
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado Lime',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 13,
            'price': 11.25
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """
        Test Creating Recipe with ingredients
        """
        ingredient1 = sample_ingredient(user=self.user)
        ingredient2 = sample_ingredient(user=self.user)

        payload = {
            'title': 'Test Recipe',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 10,
            'price': 22.66,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """
        Test updating recipe with patch
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Chocken Tika',
            'tags': [new_tag.id]
        }

        url = recipe_detail_url(recipe.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        """
        Since we created our object: recipe and then
        we update it in database using patch.
        Below function updates the object with new values
        """
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """
        Test updating a recipe with put
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spagetti',
            'time_minutes': 25,
            'price': 17
        }

        url = recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for key in payload.keys():
            self.assertEqual(getattr(recipe, key), payload[key])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
