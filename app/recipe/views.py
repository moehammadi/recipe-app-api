from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication

from core import models
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Manages Tags in Database
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated, )
    queryset = models.Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')
