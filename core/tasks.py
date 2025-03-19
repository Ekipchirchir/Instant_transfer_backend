from celery import shared_task
from django.core.management import call_command

@shared_task
def fetch_user_balances():
    # Call the management command to update the balances
    call_command('fetch_balance')
