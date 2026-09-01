from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('games/', views.games, name='games'),
    path('sessions/', views.sessions, name='sessions'),
    path('games/<int:pk>/', views.game_detail, name='game_detail'),
]    