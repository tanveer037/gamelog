from rest_framework import serializers
from .models import Game, Platform, Genre, GameSession

class GameSerializer(serializers.ModelSerializer):
    total_hours = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True, source='total_playtime')

    class Meta:
        model = Game
        fields = ['id', 'title', 'added_on', 'status', 'rating', 'platform', 'genres', 'untracked_hours', 'total_hours']