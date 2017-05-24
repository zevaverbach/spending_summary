import datetime
import os
import time
from typing import List

import math
from twilio.rest import Client as TwilioClient

from plaid import Client as PlaidClient

CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES = 5
ALERT_FOR_TRANSACTIONS_GTE = 500
MY_CELL = os.getenv('MY_CELL')
MY_TWILIO_NUM = os.getenv('MY_TWILIO_NUM')
PLAID_ENV = os.getenv('PLAID_ENV') or 'sandbox'

# this is an access ID from Plaid for a specific user and bank/credit account
PLAID_ACCESS_ID = os.getenv('PLAID_ACCESS_ID')

plaid_client = PlaidClient(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                           public_key=os.getenv('PLAID_PUBLIC_KEY'), environment=PLAID_ENV)

twilio_client = TwilioClient(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))

transaction_ids = set()


def get_all_transactions() -> List[dict]:
    today = datetime.date.today().strftime('%Y-%m-%d')
    total_transactions: int = plaid_client.Transactions.get(PLAID_ACCESS_ID, '1972-01-01', today)['total_transactions']
    all_transactions = []
    for page in range(math.ceil(total_transactions / 500)):
        all_transactions += plaid_client.Transactions.get(PLAID_ACCESS_ID, '1972-01-01', today,
                                                          offset=page * 500, count=500)['transactions']
    return all_transactions


def get_latest_transactions() -> List[dict]:
    """get 100 most recent transactions"""
    today = datetime.date.today().strftime('%Y-%m-%d')
    return [transaction
            for transaction in
            plaid_client.Transactions.get(PLAID_ACCESS_ID, '1972-01-01', today)['transactions']
            if transaction['transaction_id'] not in transaction_ids]


def alert(transaction: dict) -> None:
    message = (f'hey, a transaction hit your account that exceeds ${ALERT_FOR_TRANSACTIONS_GTE}: '
               f'{transaction["date"]} {transaction["name"]} ${transaction["amount"]}')

    twilio_client.api.account.messages.create(to=MY_CELL, from_=MY_TWILIO_NUM, body=message)


def main() -> None:
    if len(transaction_ids) == 0:
        transaction_ids.update(transaction['transaction_id'] for transaction in get_all_transactions())

    while True:

        for transaction in get_latest_transactions():

            transaction_ids.add(transaction['transaction_id'])

            if transaction['amount'] >= ALERT_FOR_TRANSACTIONS_GTE:
                alert(transaction)

        time.sleep(CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES * 60)


if __name__ == "__main__":
    main()
