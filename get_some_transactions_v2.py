import math
import os
from typing import List

# twilio.rest has a Client too, so let's avoid a namespace collision
from plaid import Client as PlaidClient

plaid_client = PlaidClient(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                           public_key=os.getenv('PLAID_PUBLIC_KEY'), environment=os.getenv('PLAID_ENV'))


# https://plaid.com/docs/api/#transactions
MAX_TRANSACTIONS_PER_PAGE = 500
OMIT_CATEGORIES = ["Transfer", "Credit Card", "Deposit"]


def get_some_transactions(access_token: str, start_date: str, end_date: str) -> List[dict]:
    account_ids = [account['account_id'] for account in plaid_client.Accounts.get(access_token)['accounts']
                   if account['subtype'] not in ['cd', 'savings']]

    num_available_transactions = plaid_client.Transactions.get(access_token, start_date, end_date,
                                                               account_ids=account_ids)['total_transactions']
    num_pages = math.ceil(num_available_transactions / MAX_TRANSACTIONS_PER_PAGE)
    transactions = []

    for page_num in range(num_pages):
        transactions += [transaction
                         for transaction in plaid_client.Transactions.get(access_token, start_date, end_date,
                                                                          account_ids=account_ids,
                                                                          offset=page_num * MAX_TRANSACTIONS_PER_PAGE,
                                                                          count=MAX_TRANSACTIONS_PER_PAGE)['transactions']
                         if transaction['category'] is None
                         or not any(category in OMIT_CATEGORIES
                                    for category in transaction['category'])]

    return transactions
