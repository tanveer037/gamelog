from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Status(models.TextChoices):
    BACKLOG = 'B', 'Backlog'
    PLAYING = 'P', 'Playing'
    FINISHED = 'F', 'Finished'
    DROPPED = 'D', 'Dropped'

class Platform(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name        

class Game(models.Model):
    title = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.BACKLOG)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name='games')
    genres = models.ManyToManyField(Genre, related_name='games', blank=True)
    def __str__(self):
        return self.title

class GameSession(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    played_on = models.DateField(auto_now_add=False)
    hours_played = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.game.title} - {self.played_on} ({self.hours_played} hours)"