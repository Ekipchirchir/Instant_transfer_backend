from django.urls import path
from .views import (
    SignupView, LoginView, LogoutView, UserDetailsView,
    TransactionListView, DepositView, WithdrawalView
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user/", UserDetailsView.as_view(), name="user_details"),
    path("transactions/", TransactionListView.as_view(), name="transaction_list"),
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", WithdrawalView.as_view(), name="withdraw"),
]
