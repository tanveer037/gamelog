from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce

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


class GameQuerySet(models.QuerySet):
    def with_hours(self):
        return self.annotate(
            total_playtime=Coalesce(Sum('sessions__duration_hours'), Value(Decimal(0)))
            + Coalesce(F('untracked_hours'), Value(Decimal(0)))
        )

class Game(models.Model):
    title = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.BACKLOG)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name='games')
    genres = models.ManyToManyField(Genre, related_name='games', blank=True)
    untracked_hours = models.DecimalField(max_digits=7, decimal_places=2, null = True, blank = True)
    objects = GameQuerySet.as_manager()

    def __str__(self):
        return self.title

class JournalEntry(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='journal')
    written_on = models.DateField()
    body = models.TextField()

    class Meta:
        ordering = ['-written_on']

    def __str__(self):
        return f"{self.game.title} - {self.written_on}"

class GameSession(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    played_on = models.DateField(auto_now_add=False)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['-played_on']

    def __str__(self):
        return f"{self.game.title} - {self.played_on} ({self.duration_hours} hours)"