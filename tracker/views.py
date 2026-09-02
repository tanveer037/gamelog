from rest_framework.viewsets import ModelViewSet
from .models import Game, GameSession
from .serializers import GameSerializer, GameSessionSerializer


class GameViewSet(ModelViewSet):
    queryset = Game.objects.prefetch_related('genres').with_hours()
    serializer_class = GameSerializer

    def _save_annotated(self, serializer):
        serializer.save()
        serializer.instance = self.get_queryset().get(pk=serializer.instance.pk)

    def perform_create(self, serializer):
        self._save_annotated(serializer)

    def perform_update(self, serializer):
        self._save_annotated(serializer)


class SessionViewSet(ModelViewSet):
    queryset = GameSession.objects.select_related('game').order_by('-played_on')
    serializer_class = GameSessionSerializer
