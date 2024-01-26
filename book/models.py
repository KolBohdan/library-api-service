from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=50, choices=CoverChoices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = [
            "title",
        ]

    def __str__(self) -> str:
        return self.title