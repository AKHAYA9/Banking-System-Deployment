from datetime import date
import os
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User, Player, Transaction, MatchResult, ContactMessage
import json
from django.contrib.auth import update_session_auth_hash
# ---------------------------
# Utility Checks
# ---------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser

# ---------------------------
# Public Views
# ---------------------------
def index(request):
    return render(request, 'pages/index.html')


def please_login(request):
    return render(request, 'auth/login.html')


def UserLogin(request):
    return render(request, 'auth/login.html')


def UserRegister(request):
    return render(request, 'auth/register.html')


# ---------------------------
# Auth Actions
# ---------------------------
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid', '').strip()
        password = request.POST.get('pswd', '').strip()

        user = authenticate(request, loginid=loginid, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['loginid'] = user.loginid
                request.session['username'] = user.username

                if user.is_staff:
                    return redirect('admin_home')
                return redirect('user_home')
            else:
                messages.warning(request, 'Your account has not yet been activated by admin.')
        else:
            messages.warning(request, 'Invalid Login ID or Password.')

    return render(request, 'auth/login.html')


def UserRegisterActions(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        loginid = request.POST.get('loginid', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validation
        if not all([username, loginid, email, mobile, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, 'auth/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/register.html')

        if User.objects.filter(loginid__iexact=loginid).exists():
            messages.error(request, "Login ID already exists.")
            return render(request, 'auth/register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'auth/register.html')

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already exists.")
            return render(request, 'auth/register.html')

        # Create user (inactive by default)
        user = User(
            username=username,
            loginid=loginid,
            email=email,
            mobile=mobile,
            is_active=False  # Admin must activate
        )
        user.set_password(password)
        user.save()

        messages.success(request, "Registration successful! Wait for admin approval.")
        return redirect('UserLogin')

    return render(request, 'auth/register.html')


def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('index')

# ---------------------------
# Admin Dashboard
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def admin_home(request):
    """Main Admin Dashboard - Shows ALL users and their player data"""
    if not request.user.is_staff:
        return redirect('UserHome')
    
    # Get all users with their player data (if exists)
    all_users = User.objects.filter(is_staff=False).select_related('player')
    
    # Get all players
    players = Player.objects.select_related('user').all()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.prefetch_related('players').all()[:10]
    
    # Calculate statistics
    total_balance = sum(player.balance for player in players)
    pending_users = User.objects.filter(is_active=False, is_staff=False).count()
    
    context = {
        'all_users': all_users,  # All registered users
        'players': players,       # All players with accounts
        'recent_transactions': recent_transactions,
        'total_players': players.count(),
        'total_balance': total_balance,
        'total_transactions': Transaction.objects.count(),
        'active_games': Transaction.objects.filter(date=date.today()).count(),
        'pending_users': pending_users,
    }
    
    return render(request, 'admin/admin_home.html', context)


# ---------------------------
# User Management (NEW)
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def manage_users(request):
    """View to manage all registered users"""
    pending_users = User.objects.filter(is_active=False, is_staff=False)
    active_users = User.objects.filter(is_active=True, is_staff=False).select_related('player')
    
    context = {
        'pending_users': pending_users,
        'active_users': active_users,
    }
    
    return render(request, 'admin/manage_users.html', context)


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def activate_user(request, user_id):
    """Activate user and create player account"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    
    # Player will be auto-created by signal
    messages.success(request, f"User {user.username} activated successfully!")
    return redirect('manage_users')


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def deactivate_user(request, user_id):
    """Deactivate user"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    
    messages.success(request, f"User {user.username} deactivated successfully!")
    return redirect('manage_users')


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Delete user and associated player"""
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()  # Player will be deleted automatically (CASCADE)
    
    messages.success(request, f"User {username} deleted successfully!")
    return redirect('manage_users')


# ---------------------------
# Player CRUD (Updated)
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def add_player(request):
    """Manually add player for a user"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        balance = request.POST.get('balance', 0)
        
        user = get_object_or_404(User, id=user_id)
        
        # Check if player already exists
        if hasattr(user, 'player'):
            messages.warning(request, f"Player account already exists for {user.username}")
            return redirect('admin_home')
        
        Player.objects.create(
            user=user,
            name=name,
            balance=balance
        )
        messages.success(request, f"Player account created for {user.username}")
        return redirect('admin_home')
    
    # Get users without player accounts
    users_without_players = User.objects.filter(
        is_staff=False, 
        is_active=True
    ).exclude(player__isnull=False)
    
    return render(request, 'admin/add_player.html', {'users': users_without_players})


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def update_player_balance(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == 'POST':
        new_balance = Decimal(request.POST.get('balance'))
        player.balance = new_balance
        player.save()
        messages.success(request, f"{player.name}'s balance updated to ₹{new_balance}.")
        return redirect('admin_home')
    return render(request, 'admin/update_player.html', {'player': player})


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def delete_player(request, pk):
    """Delete player (not the user)"""
    player = get_object_or_404(Player, pk=pk)
    player_name = player.name
    player.delete()
    messages.success(request, f"Player account for {player_name} deleted.")
    return redirect('admin_home')


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def reset_player_balance(request, pk):
    player = get_object_or_404(Player, pk=pk)
    player.balance = Decimal('0.00')
    player.save()
    messages.success(request, f"{player.name}'s balance reset to ₹0.00.")
    return redirect('admin_home')


# ---------------------------
# Transaction CRUD
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def add_transaction(request):
    if request.method == 'POST':
        operation = request.POST.get('operation')
        entry_fee = Decimal(request.POST.get('entry_fee'))
        total_win = Decimal(request.POST.get('total_win'))
        position = request.POST.get('position')
        time_slot = request.POST.get('time_slot')
        trans_date = request.POST.get('date')
        player_ids = request.POST.getlist('players')

        players = Player.objects.filter(id__in=player_ids)

        if len(players) != 4:
            messages.error(request, 'Please select exactly 4 players!')
            return redirect('admin_home')

        tx = Transaction.objects.create(
            operation=operation,
            entry_fee=entry_fee,
            total_win=total_win,
            position=position,
            time_slot=time_slot,
            date=trans_date
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

        messages.success(request, "Transaction added successfully.")
        return redirect('admin_home')

    players = Player.objects.all()
    # ADD THIS LINE TO PASS TODAY'S DATE
    context = {
        'players': players,
        'today': date.today()  # Add this
    }
    return render(request, 'admin/add_transaction.html', context)


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tx.delete()
    messages.success(request, "Transaction deleted successfully.")
    return redirect('admin_home')


# ---------------------------
# Reset Functions
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def reset_transactions(request):
    Transaction.objects.all().delete()
    messages.success(request, "All match transactions have been reset!")
    return redirect('admin_home')


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def reset_all(request):
    Transaction.objects.all().delete()
    Player.objects.update(balance=0)
    messages.success(request, "All transactions cleared and player balances reset!")
    return redirect('admin_home')


# ---------------------------
# Match Results
# ---------------------------
@login_required(login_url='please_login')
@user_passes_test(is_admin)
def match_results(request):
    if request.method == 'POST':
        result_date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        description = request.POST.get('description')
        screenshot = request.FILES.get('screenshot')

        if screenshot and result_date and time_slot:
            ext = os.path.splitext(screenshot.name)[1]
            clean_time = time_slot.replace(' ', '').replace(':', '')
            base_filename = f"{result_date}_{clean_time}"
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
                date=result_date,
                time_slot=time_slot,
                description=description,
                screenshot=saved_path
            )
            
            messages.success(request, 'Match result uploaded successfully.')

    results = MatchResult.objects.order_by('-date')
    return render(request, 'admin/match_results.html', {'results': results})


@login_required(login_url='please_login')
@user_passes_test(is_admin)
def delete_match_result(request, result_id):
    result = get_object_or_404(MatchResult, id=result_id)
    result.delete()
    messages.success(request, "Match result deleted successfully.")
    return redirect('match_results')


# ---------------------------
# Public Pages
# ---------------------------
def service(request):
    return render(request, 'pages/services.html')


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    return render(request, "pages/contact.html")


def contact_submit(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            message = data.get("message")

            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )

            return JsonResponse({
                "status": "success",
                "message": "Thank you! Your message has been sent."
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error: {str(e)}"
            }, status=400)

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=400)

@login_required(login_url='please_login')
def UserHome(request):
    """Main user dashboard showing transactions and stats"""
    # Get or create player for logged-in user
    player, created = Player.objects.get_or_create(
        user=request.user,
        defaults={'name': request.user.username, 'balance': 0}
    )

    # User-specific transactions
    user_transactions = Transaction.objects.filter(players=player).order_by('-date')

    # Calculate statistics
    total_transactions = user_transactions.count()
    total_wins = user_transactions.filter(operation='+').count()
    games_played = user_transactions.count()

    context = {
        'player': player,
        'transactions': user_transactions,
        'total_transactions': total_transactions,
        'total_wins': total_wins,
        'games_played': games_played,
    }

    return render(request, 'user/user_home.html', context)


@login_required
def UserProfileUpdateView(request):
    """Update user profile information"""
    user = request.user
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation
        if not all([username, email, mobile]):
            messages.error(request, "Username, email, and mobile are required.")
            return render(request, 'user/profile_edit.html')
        
        # Check if username is taken by another user
        if User.objects.filter(username__iexact=username).exclude(id=user.id).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'user/profile_edit.html')
        
        # Check if email is taken by another user
        if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'user/profile_edit.html')
        
        # Check if mobile is taken by another user
        if User.objects.filter(mobile=mobile).exclude(id=user.id).exists():
            messages.error(request, "Mobile number already exists.")
            return render(request, 'user/profile_edit.html')
        
        # Update basic information
        user.username = username
        user.email = email
        user.mobile = mobile
        
        # Handle password change if provided
        if current_password or new_password or confirm_password:
            if not current_password:
                messages.error(request, "Current password is required to change password.")
                return render(request, 'user/profile_edit.html')
            
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
                return render(request, 'user/profile_edit.html')
            
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return render(request, 'user/profile_edit.html')
            
            if len(new_password) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
                return render(request, 'user/profile_edit.html')
            
            # Set new password
            user.set_password(new_password)
            
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            
            messages.success(request, "Profile and password updated successfully!")
        else:
            messages.success(request, "Profile updated successfully!")
        
        user.save()
        return redirect('user_home')
    
    return render(request, 'user/profile_edit.html')


@login_required
def UserChangePasswordView(request):
    """Separate view for changing password only"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, "All password fields are required.")
            return render(request, 'user/change_password.html')
        
        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'user/change_password.html')
        
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'user/change_password.html')
        
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'user/change_password.html')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Keep user logged in
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Password changed successfully!")
        return redirect('user_home')
    
    return render(request, 'user/change_password.html')