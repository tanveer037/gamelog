from django.contrib import admin
from django.utils.text import Truncator
from .models import Game, Platform, Genre, GameSession, JournalEntry


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
    list_display = ['id', 'game', 'played_on', 'duration_hours']
    list_filter = ['played_on', 'game']
    search_fields = ['game__title']
    list_select_related = ['game']
    autocomplete_fields = ['game']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'written_on', 'excerpt']
    list_filter = ['written_on', 'game']
    search_fields = ['body', 'game__title']
    list_select_related = ['game']
    autocomplete_fields = ['game']

    @admin.display(description='Entry')
    def excerpt(self, entry):
        return Truncator(entry.body).chars(80)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']