from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('games/', views.GameList.as_view(), name='games'),
    path('sessions/', views.SessionList.as_view(), name='sessions'),
    path('games/<int:pk>/', views.GameDetail.as_view(), name='game_detail'),
]    