from django.db import models
from django.contrib.auth.models import \
    AbstractBaseUser,\
    BaseUserManager,\
    PermissionsMixin


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
