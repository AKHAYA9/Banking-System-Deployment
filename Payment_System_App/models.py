from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================================
# PLAYER MODEL - NOW LINKED TO USER
# ==========================================
class Player(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='player', null=True, blank=True)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} - ₹{self.balance}"

    class Meta:
        ordering = ['-balance']


# ==========================================
# TRANSACTION MODEL
# ==========================================
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
    date = models.DateField()
    players = models.ManyToManyField(Player)
    operation = models.CharField(max_length=1, choices=OPERATION_CHOICES)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_win = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    position = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.time_slot} | {self.date} | ₹{self.total_win or self.entry_fee}"
    
    class Meta:
        ordering = ['-created_at']


# ==========================================
# MATCH RESULT MODEL
# ==========================================
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
    
    class Meta:
        ordering = ['-date']


# ==========================================
# CUSTOM USER MANAGER
# ==========================================
class CustomUserManager(BaseUserManager):
    def create_user(self, loginid, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not loginid:
            raise ValueError('Users must have a login ID')
        
        email = self.normalize_email(email)
        user = self.model(loginid=loginid, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, loginid, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(loginid, email, password, **extra_fields)


# ==========================================
# CUSTOM USER MODEL
# ==========================================
class User(AbstractBaseUser, PermissionsMixin):
    loginid = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True)

    # Optional fields for address
    locality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    # Permissions & status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'loginid'
    REQUIRED_FIELDS = ['email', 'username']

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# ==========================================
# AUTO-CREATE PLAYER WHEN USER IS ACTIVATED
# ==========================================
@receiver(post_save, sender=User)
def create_player_for_user(sender, instance, created, **kwargs):
    """
    Automatically create a Player account when:
    1. A new user is created and activated by admin
    2. An existing user is activated by admin
    """
    if instance.is_active and not instance.is_staff:
        # Check if player doesn't exist
        if not hasattr(instance, 'player'):
            Player.objects.create(
                user=instance,
                name=instance.username,
                balance=0
            )


# ==========================================
# CONTACT MESSAGE MODEL
# ==========================================
class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']