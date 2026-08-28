from django.contrib import admin
from .models import Game, Platform, Genre, GameSession


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'status', 'rating', 'added_on']
    list_editable = ['status', 'rating']
    list_filter = ['status', 'platform', 'genres']
    search_fields = ['title']
    ordering = ['title']
    list_select_related = ['platform']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['game', 'played_on', 'hours_played']
    list_filter = ['played_on', 'game']
    ordering = ['-played_on']
    list_select_related = ['game']


admin.site.register(Platform)
admin.site.register(Genre)