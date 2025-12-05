from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ContactMessage, Player, Transaction, MatchResult,User, CustomUserManager
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')
    
@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ("date", "time_slot", "screenshot", "description")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('time_slot', 'date', 'operation', 'entry_fee', 'total_win', 'position', 'created_at')
    filter_horizontal = ('players',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("loginid", "email", "username", "mobile", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("loginid", "email", "password")}),
        ("Personal Info", {"fields": ("username", "mobile", "locality", "address", "city", "state")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("loginid", "email", "username", "mobile", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    search_fields = ("loginid", "email", "username")
    ordering = ("loginid",)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "message", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)