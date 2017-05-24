import datetime
import math
import os
from typing import List

from twilio.rest import Client as TwilioClient

from plaid import Client as PlaidClient

# these are access IDs from Plaid for a specific bank/credit account
ACCOUNT_ACCESS_IDS: List[str] = [os.getenv('PLAID_ACCESS_ID'), os.getenv('OTHER_PLAID_ACCESS_ID')]
MAX_TRANSACTIONS_PER_PAGE = 500

plaid_client = PlaidClient(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                           public_key=os.getenv('PLAID_PUBLIC_KEY'), environment=os.getenv('PLAID_ENV'))

twilio_client = TwilioClient(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))


def get_num_available_transactions(access_id, start: str, end: str) -> int:
    return plaid_client.Transactions.get(access_id, start, end)['total_transactions']


def get_transactions_from_account(access_id: str, start: str, end: str) -> List[dict]:
    transactions = []
    num_available_transactions = get_num_available_transactions(access_id, start, end)
    num_pages = math.ceil(num_available_transactions / MAX_TRANSACTIONS_PER_PAGE)

    for page_num in range(num_pages):
        transactions += plaid_client.Transactions.get(access_id, start, end,
                                                      offset=page_num * MAX_TRANSACTIONS_PER_PAGE,
                                                      count=MAX_TRANSACTIONS_PER_PAGE)['transactions']

    return transactions


def get_transactions_from_multiple_accounts(access_ids: List[str], start: str, end: str) -> List[dict]:
    transactions = []
    for access_id in access_ids:
        transactions += get_transactions_from_account(access_id, start, end)
    return transactions


def get_yesterdays_transactions() -> List[dict]:
    yesterday: str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return get_transactions_from_multiple_accounts(ACCOUNT_ACCESS_IDS, yesterday, yesterday)


def send_summary(transactions: List[dict]) -> None:
    total_spent = sum(transaction['amount']
                      for transaction in transactions
                      if transaction['amount'] > 0)

    message = f'You spent ${total_spent} yesterday. 💸'

    twilio_client.api.account.messages.create(to=os.getenv('MY_CELL'), from_=os.getenv('MY_TWILIO_NUM'), body=message)


if __name__ == "__main__":
    send_summary(get_yesterdays_transactions())
