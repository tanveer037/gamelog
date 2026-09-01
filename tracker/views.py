import code

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Game, GameSession
from .serializers import GameSerializer, GameSessionSerializer
from django.shortcuts import get_object_or_404 

def index(request):
    return HttpResponse("Hello, World!")

@api_view(['GET', 'POST'])
def games(request):
    if request.method == 'GET':
        games = Game.objects.prefetch_related('genres').with_hours()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            game = serializer.save()
            game = Game.objects.with_hours().get(pk=game.pk)
            return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def sessions(request):
    if request.method == 'GET':
        sessions = GameSession.objects.select_related('game').order_by('-played_on')
        serializer = GameSessionSerializer(sessions, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
def game_detail(request, pk):
    game = get_object_or_404(Game.objects.with_hours(), pk=pk)

    if request.method == 'GET':
        return Response(GameSerializer(game).data)

    if request.method == 'PATCH':
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            game = serializer.save()
            game = Game.objects.with_hours().get(pk=game.pk)
            return Response(GameSerializer(game).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    if request.method == 'DELETE':
        game.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    