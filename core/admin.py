from django.contrib import admin
from .models import User, APIToken, Transaction, Deposit, Withdrawal, WebSocketSession

admin.site.register(User)
admin.site.register(APIToken)
admin.site.register(Transaction)
admin.site.register(Deposit)
admin.site.register(Withdrawal)
admin.site.register(WebSocketSession)
