import os
from django.shortcuts import render
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import MatchResult, Player, Transaction
from django.contrib import messages
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def home(request):
    players = Player.objects.all()
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'players': players, 'transactions': transactions})


def add_transaction(request):
    if request.method == 'POST':
        operation = request.POST.get('operation')
        entry_fee = Decimal(request.POST.get('entry_fee'))
        total_win = Decimal(request.POST.get('total_win'))
        position = request.POST.get('position')
        time_slot = request.POST.get('time_slot')
        date = request.POST.get('date')
        player_ids = request.POST.getlist('players')

        players = Player.objects.filter(id__in=player_ids)

        if len(players) != 4:
            return render(request, 'error.html', {'message': 'Please select exactly 4 players!'})

        tx = Transaction.objects.create(
            operation=operation,
            entry_fee=entry_fee,
            total_win=total_win,
            position=position,
            time_slot=time_slot,
            date=date
        )
        tx.players.set(players)
        tx.save()

        split_amount = (total_win - entry_fee) / Decimal(4)

        for player in players:
            if operation == '+':
                player.balance += split_amount
            else:
                player.balance -= entry_fee / Decimal(4)
            player.save()

        return redirect('home')

    players = Player.objects.all()
    return render(request, 'add_transaction.html', {'players': players})

def add_player(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Player.objects.create(name=name)
        messages.success(request, f"Player {name} added successfully.")
        return redirect('home')
    return render(request, 'add_player.html')


def delete_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    player.delete()
    messages.success(request, f"Player {player.name} deleted.")
    return redirect('home')

def update_player_balance(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == 'POST':
        new_balance = Decimal(request.POST.get('balance'))
        player.balance = new_balance
        player.save()
        messages.success(request, f"{player.name}'s balance updated to ₹{new_balance}.")
        return redirect('home')

    return render(request, 'update_player.html', {'player': player})


def reset_player_balance(request, pk):
    player = get_object_or_404(Player, pk=pk)
    player.balance = Decimal('0.00')
    player.save()
    messages.success(request, f"{player.name}'s balance reset to ₹0.00.")
    return redirect('home')

def reset_transactions(request):
    Transaction.objects.all().delete()
    messages.success(request, "✅ All match transactions have been reset!")
    return redirect('home')


def reset_all(request):
    Transaction.objects.all().delete()
    Player.objects.update(balance=0)
    messages.success(request, "💥 All transactions cleared and player balances reset!")
    return redirect('home')

def match_results(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        description = request.POST.get('description')
        screenshot = request.FILES.get('screenshot')

        if screenshot and date and time_slot:

            ext = os.path.splitext(screenshot.name)[1]
            clean_time = time_slot.replace(' ', '').replace(':', '')
            base_filename = f"{date}_{clean_time}"
            new_filename = f"{base_filename}{ext}"

            counter = 1
            while default_storage.exists(f"match_results/{new_filename}"):
                new_filename = f"{base_filename}_{counter}{ext}"
                counter += 1

            saved_path = default_storage.save(
                f"match_results/{new_filename}",
                ContentFile(screenshot.read())
            )

            MatchResult.objects.create(
                date=date,
                time_slot=time_slot,
                description=description,
                screenshot=saved_path
            )

        return redirect('match_results')

    results = MatchResult.objects.order_by('-date')
    return render(request, 'match_results.html', {'results': results})

def update_match_result(request):
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        description = request.POST.get('description')
        screenshot = request.FILES.get('screenshot')

        match = MatchResult.objects.get(id=match_id)
        match.date = date
        match.time_slot = time_slot
        match.description = description
        if screenshot:
            match.screenshot = screenshot
        match.save()

        return redirect('match_results')
    


def delete_match_result(request, result_id):
    result = get_object_or_404(MatchResult, id=result_id)
    result.delete()
    return redirect('match_results')


def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, id=pk)

    if request.method == "POST":
        tx.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect('dashboard')  # 🔥 change to your transactions page

    return render(request, "confirm_delete_transaction.html", {"tx": tx})