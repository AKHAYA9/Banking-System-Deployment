from django.contrib import admin

from .models import Player, Transaction, MatchResult
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')
@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_slot', 'description')
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('time_slot', 'date', 'operation', 'entry_fee', 'total_win', 'position', 'created_at')
    filter_horizontal = ('players',)