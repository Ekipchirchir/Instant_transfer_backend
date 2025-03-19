from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

# ✅ Define Currency Choices Globally
CURRENCY_CHOICES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("BTC", "Bitcoin"),
    ("ETH", "Ethereum"),
    ("USDT", "Tether"),
]

# ✅ Custom User Model
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)  # User's name from Deriv
    deriv_account = models.CharField(max_length=255, unique=True)  # Deriv account number
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # User's balance
    # Add other fields as needed

    # ✅ Fix group conflicts by renaming related names
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="core_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="core_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.username


# ✅ API Token Model
class APIToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="api_token"
    )
    access_token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return now() >= self.expires_at

    def __str__(self):
        return f"API Token for {self.user.username}"


# ✅ Transaction Model (For Both Deposits & Withdrawals)
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=100, unique=True)

    # ✅ Use Global Currency Choices
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} {self.currency} by {self.user.username}"


# ✅ Deposit Model
class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deposits")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("completed", "Completed")], default="pending")
    deriv_transaction_id = models.CharField(max_length=100, unique=True)

    # ✅ Use Global Currency Choices
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit {self.deriv_transaction_id} - {self.amount} {self.currency}"


# ✅ Withdrawal Model
class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("completed", "Completed")], default="pending")
    deriv_transaction_id = models.CharField(max_length=100, unique=True)

    # ✅ Use Global Currency Choices
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal {self.deriv_transaction_id} - {self.amount} {self.currency}"


# ✅ WebSocket Session Model (For Real-Time Updates)
class WebSocketSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ws_sessions")
    session_id = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WebSocket Session {self.session_id} - {self.user.username}"
