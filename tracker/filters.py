from django_filters.rest_framework import FilterSet
from .models import Game


class GameFilter(FilterSet):

    class Meta:
        model = Game
        fields = ['status', 'platform', 'genres']
