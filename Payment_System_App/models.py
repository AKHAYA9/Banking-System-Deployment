from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    OPERATION_CHOICES = [
        ('+', 'Add'),
        ('-', 'Subtract'),
    ]

    time_slot = models.CharField(max_length=10, choices=[
        ('12PM', '12 PM'), ('3PM', '3 PM'), ('6PM', '6 PM'),
        ('8PM', '8 PM'), ('9PM', '9 PM'), ('11PM', '11 PM'),
        ('12AM', '12 AM'),
    ])
    date = models.DateField()  # ✅ New Field

    players = models.ManyToManyField(Player)
    operation = models.CharField(max_length=1, choices=OPERATION_CHOICES)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_win = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    position = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.time_slot} | {self.date} | ₹{self.total_win or self.entry_fee}"
    
class MatchResult(models.Model):
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=[
        ('12PM', '12 PM'), ('3PM', '3 PM'), ('6PM', '6 PM'),
        ('8PM', '8 PM'), ('9PM', '9 PM'), ('11PM', '11 PM'),
        ('12AM', '12 AM'),
    ])
    screenshot = models.ImageField(upload_to='match_results/')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.time_slot}"