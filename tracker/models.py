from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count, Avg, Sum, F, Value
from django.db.models.functions import Coalesce
from django.conf import settings


class Status(models.TextChoices):
    BACKLOG = 'B', 'Backlog'
    PLAYING = 'P', 'Playing'
    FINISHED = 'F', 'Finished'
    DROPPED = 'D', 'Dropped'


class GameQuerySet(models.QuerySet):
    def with_stats(self):
        return self.annotate(
            mean_rating=Avg('library_entries__rating'),
            owner_count=Count('library_entries'),
        )


class Game(models.Model):
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField('Genre', related_name='games', blank=True)
    release_year = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1958), MaxValueValidator(2100)],
    )

    objects = GameQuerySet.as_manager()

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Platform(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LibraryEntryQuerySet(models.QuerySet):
    def with_hours(self):
        return self.annotate(
            total_playtime=Coalesce(Sum('sessions__duration_hours'), Value(Decimal(0)))
            + Coalesce(F('untracked_hours'), Value(Decimal(0)))
        )


class LibraryEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library'
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='library_entries')
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name='library_entries')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.BACKLOG)
    rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    untracked_hours = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    objects = LibraryEntryQuerySet.as_manager()

    class Meta:
        unique_together = [['user', 'game']]
        ordering = ['-added_on']

    def __str__(self):
        return f"{self.user.username} — {self.game.title}"


class GameSession(models.Model):
    library_entry = models.ForeignKey(
        LibraryEntry, on_delete=models.CASCADE, related_name='sessions'
    )
    played_on = models.DateField()
    duration_hours = models.DecimalField(
        max_digits=4, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-played_on']

    def __str__(self):
        return f"{self.library_entry.game.title} - {self.played_on} ({self.duration_hours} hours)"


class Review(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    body = models.TextField()
    written_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['game', 'user']]
        ordering = ['-written_on']

    def __str__(self):
        return f"Review of {self.game.title} by {self.user.username}"
