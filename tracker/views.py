from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer

def index(request):
    return HttpResponse("Hello, World!")

@api_view(['GET'])
def games(request):
    games = Game.objects.prefetch_related('genres').with_hours()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)
