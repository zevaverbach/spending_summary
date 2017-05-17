import os

import plaid


plaid_client = plaid.Client(
    client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'), public_key=os.getenv('PLAID_PUBLIC_KEY'),
    environment='sandbox')
