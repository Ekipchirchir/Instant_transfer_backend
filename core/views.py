import logging
import json
import requests
from datetime import timedelta
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from django.views import View
from .models import APIToken, Transaction, Deposit, Withdrawal
from .serializers import (
    UserSerializer, APITokenSerializer, TransactionSerializer, 
    DepositSerializer, WithdrawalSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

DERIV_API_URL = "https://api.deriv.com/api/v2"
DERIV_APP_ID = "70029"  # Ensure this is correct

# ✅ User Signup
class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ User Login
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ User Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

# ✅ Get User Details
class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

# ✅ Transaction History
class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user).order_by("-created_at")
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ✅ Redirect to Deriv Login
class DerivLoginView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_uri = "https://thu-cabin-roulette-anthropology.trycloudflare.com/callback/"
        deriv_login_url = f"https://oauth.deriv.com/oauth2/authorize?app_id={DERIV_APP_ID}&redirect_uri={redirect_uri}"
        return redirect(deriv_login_url)

# ✅ Deriv OAuth Callback (Redirect to Home Screen after Login)
class DerivCallbackView(View):
    def get(self, request, *args, **kwargs):
        deriv_token = request.GET.get("token1", "").strip()
        account = request.GET.get("acct1", "").strip()

        if not deriv_token or not account:
            return redirect("http://localhost:8081/auth-failed?error=Missing+token+or+account")

        user_info = self.get_deriv_user_info(deriv_token)

        if "error" in user_info:
            return redirect("http://localhost:8081/auth-failed?error=Invalid+Deriv+token")

        request.session["deriv_user"] = user_info

        redirect_url = f"http://localhost:8081/auth-success?access_token={deriv_token}&deriv_account={account}"
        return redirect(redirect_url)

    def get_deriv_user_info(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{DERIV_API_URL}/account"

        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                return {"error": "Invalid response from Deriv"}
        except Exception as e:
            return {"error": str(e)}

# ✅ Get Deriv Account Balance
def get_deriv_balance(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{DERIV_API_URL}/balance"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if response.status_code == 200:
            return data.get("balance", {}).get("balance", 0.00)
        else:
            return {"error": data}
    except Exception as e:
        return {"error": str(e)}

# ✅ Validate Deriv Token
def validate_deriv_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{DERIV_API_URL}/account"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if response.status_code == 200:
            return data
        else:
            raise Exception("Invalid token")
    except Exception as e:
        raise Exception(str(e))

# ✅ Deposit Funds
class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        currency = request.data.get("currency", "USD")

        if not amount or float(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        transaction_id = f"DEP{now().timestamp()}"

        deposit = Deposit.objects.create(
            user=user, amount=amount, currency=currency, status="pending", deriv_transaction_id=transaction_id
        )
        return redirect("http://localhost:8081/deposit-success")

# ✅ Withdraw Funds
class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        currency = request.data.get("currency", "USD")

        if not amount or float(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        transaction_id = f"WDR{now().timestamp()}"

        withdrawal = Withdrawal.objects.create(
            user=user, amount=amount, currency=currency, status="pending", deriv_transaction_id=transaction_id
        )
        return redirect("http://localhost:8081/withdrawal-success")
