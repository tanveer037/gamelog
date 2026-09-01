from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, GameSession
from .serializers import GameSerializer, GameSessionSerializer
from django.shortcuts import get_object_or_404 

def index(request):
    return HttpResponse("Hello, World!")

class GameList(APIView):
    def get(self, request):
        games = Game.objects.prefetch_related('genres').with_hours()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            game = serializer.save()
            game = Game.objects.with_hours().get(pk=game.pk)
            return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameDetail(APIView):
    def get_object(self, pk):
        return get_object_or_404(Game.objects.with_hours(), pk=pk)

    def get(self, request, pk):
        game = self.get_object(pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def patch(self, request, pk):
        game = self.get_object(pk)
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            game = serializer.save()
            game = Game.objects.with_hours().get(pk=game.pk)
            return Response(GameSerializer(game).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        game = self.get_object(pk)
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    


class SessionList(APIView):
    def get(self, request):
        sessions = GameSession.objects.select_related('game').order_by('-played_on')
        serializer = GameSessionSerializer(sessions, many=True)
        return Response(serializer.data)
