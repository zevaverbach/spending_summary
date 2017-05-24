import os
from typing import List

# twilio.rest has a Client too, so let's avoid a namespace collision
from plaid import Client as PlaidClient

plaid_client = PlaidClient(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                           public_key=os.getenv('PLAID_PUBLIC_KEY'), environment=os.getenv('PLAID_ENV'))


def get_some_transactions(access_token: str, start_date: str, end_date: str) -> List[dict]:
    return plaid_client.Transactions.get(access_token, start_date, end_date)
