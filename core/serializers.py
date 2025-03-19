from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIToken, Transaction, Deposit, Withdrawal

User = get_user_model()

# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "deriv_account", "balance", "default_currency"]

# ✅ API Token Serializer
class APITokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = ["access_token", "expires_at"]

# ✅ Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "user", "amount", "transaction_type", "status", "transaction_id", "currency", "created_at"]

# ✅ Deposit Serializer
class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ["id", "user", "amount", "status", "deriv_transaction_id", "currency", "created_at"]

# ✅ Withdrawal Serializer
class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id", "user", "amount", "status", "deriv_transaction_id", "currency", "created_at"]
