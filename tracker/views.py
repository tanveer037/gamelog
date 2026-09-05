from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Game, GameSession, JournalEntry
from .serializers import GameSerializer, GameSessionSerializer, JournalEntrySerializer
from .filters import GameFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404


class GameViewSet(ModelViewSet):
    queryset = Game.objects.prefetch_related('genres').with_hours()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GameFilter
    search_fields = ['title']
    ordering_fields = ['title', 'added_on', 'rating', 'total_playtime']
    ordering = ['title']

    serializer_class = GameSerializer

    def _save_annotated(self, serializer):
        serializer.save()
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer):
        self._save_annotated(serializer)

    def perform_update(self, serializer):
        self._save_annotated(serializer)


class SessionViewSet(ModelViewSet):
    queryset = GameSession.objects.select_related('game')
    serializer_class = GameSessionSerializer


class NestedSessionViewSet(ReadOnlyModelViewSet):
    serializer_class = GameSessionSerializer

    def get_queryset(self):
        return (GameSession.objects
                .filter(game_id=self.kwargs['game_pk'])
                .select_related('game'))       

class JournalViewSet(ModelViewSet):
    serializer_class = JournalEntrySerializer

    def get_queryset(self):
        return JournalEntry.objects.filter(game_id=self.kwargs['game_pk']).select_related('game')

    def perform_create(self, serializer):
        game = get_object_or_404(Game, pk=self.kwargs['game_pk'])
        serializer.save(game=game)

    def get_view_name(self):
        game_pk = getattr(self, 'kwargs', {}).get('game_pk')
        game = Game.objects.filter(pk=game_pk).first() if game_pk else None
        return f'Journal — {game.title}' if game else 'Journal'    