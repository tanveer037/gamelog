from django.contrib import admin
from .models import Game, Platform, Genre, GameSession


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'platform', 'status', 'rating', 'untracked_hours', 'added_on', 'total_playtime']
    list_display_links = ['title']
    list_editable = ['status', 'rating', 'untracked_hours']
    list_filter = ['status', 'platform', 'genres']
    search_fields = ['title']
    ordering = ['title']
    list_select_related = ['platform']
    filter_horizontal = ['genres']

    def get_queryset(self, request):
        return super().get_queryset(request).with_hours()

    @admin.display(ordering='total_playtime', description='Total hours')
    def total_playtime(self, game):
        return game.total_playtime


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['game', 'played_on', 'duration_hours']
    list_filter = ['played_on', 'game']
    ordering = ['-played_on']
    list_select_related = ['game']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']