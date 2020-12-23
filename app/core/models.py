from django.db import models
from django.contrib.auth.models import \
    AbstractBaseUser, \
    BaseUserManager, \
    PermissionsMixin
from django.conf import settings
import uuid
import os


def recipe_image_file_path(instance, file_name):
    """
    Generate filepath for new recipe image
    :param instance:
    :param file_name:
    :return: String
    """
    extension = file_name.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{extension}'
    return os.path.join('uploads/recipe/', file_name)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user with email
        :param email:
        :param password:
        :param extra_fields:
        :return: User
        """
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if not email:
            raise ValueError('User must have an email address')
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new superuser
        :param email:
        :param password:
        :return: User
        """
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign user manager to objects
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """
    Tag to be used for a recipe
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingredients to be used for recipe
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Recipe Object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        """
        Returns a string representation for recipe instance
        """
        return self.title
