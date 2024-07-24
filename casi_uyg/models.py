from django.db import models

# Create your models here.
from django.db import models

class BetHistory(models.Model):
    bet_number = models.BigIntegerField(null=True, blank=True)
    bet_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    game = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Bet {self.bet_number} - {self.bet_time} - {self.game} - {self.amount}"

class BetHistory2(models.Model):
    bet_number = models.BigIntegerField(null=True, blank=True)
    bet_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    game = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Bet {self.bet_number} - {self.bet_time} - {self.game} - {self.amount}"
