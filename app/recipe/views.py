from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication

from core import models
from recipe import serializers


class TagViewSet(
                viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.CreateModelMixin):
    """
    Manages Tags in Database
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated,)
    queryset = models.Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Create a new Tag
        :param serializer:
        :return: Tag
        """
        serializer.save(user=self.request.user)


class IngredientsViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    """
    Manages Ingredients in Database
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')

    def perform_create(self, serializer):
        """
        Creates a new ingredient
        :param serializer:
        :return: Ingredient
        """
        return serializer.save(user=self.request.user)
