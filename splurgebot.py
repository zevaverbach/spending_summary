import datetime
import os
import time
from twilio.rest import Client as TwilioClient

import plaid

CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES = 5
ALERT_FOR_TRANSACTIONS_GTE = 500
MY_CELL = os.getenv('MY_CELL')
MY_TWILIO_NUM = os.getenv('MY_TWILIO_NUM')

plaid_client = plaid.Client(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                            public_key=os.getenv('PLAID_PUBLIC_KEY'), environment=os.getenv('PLAID_ENV'))
twilio_client = TwilioClient(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))

# this is an access ID from Plaid for a specific user and bank/credit account
PLAID_ACCESS_ID = os.getenv('PLAID_ACCESS_ID')

transaction_ids = set()


def get_latest_transactions():
    today = datetime.date.tody().strftime('%Y-%m-%d')
    return [transaction
            for transaction in plaid_client.Transactions.get(PLAID_ACCESS_ID, '1972-01-01', today)['transactions']
            if transaction['transaction_id'] not in transaction_ids]


def alert(transaction):
    message = (f'hey, a transaction hit your account that exceeds ${ALERT_FOR_TRANSACTIONS_GTE}: ' 
               f'{transaction["date"]} {transaction["name"]} ${transaction["amount"]}')
    twilio_client.api.account.messages.create(to=MY_CELL, from_=MY_TWILIO_NUM, body=message)


def main():
    while True:
        for transaction in get_latest_transactions():
            transaction_ids.add(transaction['transaction_id'])
            if transaction['amount'] >= ALERT_FOR_TRANSACTIONS_GTE:
                alert(transaction)

        time.sleep(CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES * 60)


if __name__ == "__main__":
    main()
