from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from core import models


def sample_user(email='test@test.com', password='test@123'):
    """
    Create a sample user
    :param email:
    :param password:
    :return: User
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test Creating a new user with an email is successfull
        """
        email = "test@test.com"
        password = "test@123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email for a new user is normalized
        """
        email = "test@SDFS.COM"
        user = get_user_model().objects.create_user(email, 'test@123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test Creating users with no emails raising error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test')

    def test_create_new_super_user(self):
        """
        Test creating a new super user
        """
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
        Test the tag string representation
        """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """
        Test the ingredient string representation
        """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucamber'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
        Test the recipe string representation
        """
        user = sample_user()

        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Cucamber'
        )
        tag = models.Tag.objects.create(
            user=user,
            name='Vegan'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Steak and Mushroom',
            time_minutes=5,
            link='test-recipe.com',
            price=25.36
        )
        recipe.ingredients.add(ingredient)
        recipe.tags.add(tag)
        recipe.save()

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """
        Test that image is save in the correct location
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimgae.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
