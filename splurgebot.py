import datetime
import os
import time

import plaid

CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES = 5
ALERT_FOR_TRANSACTIONS_GTE = 500

c = plaid.Client(client_id=os.getenv('PLAID_CLIENT_ID'), secret=os.getenv('PLAID_SECRET'),
                            public_key=os.getenv('PLAID_PUBLIC_KEY'), environment='development')

ACCESS_ID = 'access id for a specific account and user from Plaid'

transaction_ids = set()


def get_latest_transactions():
    today = datetime.date.today().strftime('%Y-%m-%d')
    return [transaction
            for transaction in c.Transactions.get(ACCESS_ID, '1972-01-01', today)['transactions']
            if transaction['transaction_id'] not in transaction_ids]


def alert(transaction):
    print(f'hey, a transaction hit your account that exceeds ${ALERT_FOR_TRANSACTIONS_GTE}:')
    print(f'{transaction["date"]} {transaction["name"]} ${transaction["amount"]}')


def main():
    while True:
        for transaction in get_latest_transactions():
            transaction_ids.add(transaction['transaction_id'])
            if transaction['amount'] >= ALERT_FOR_TRANSACTIONS_GTE:
                alert(transaction)

        time.sleep(CHECK_FOR_NEW_TRANSACTIONS_EVERY_X_MINUTES * 60)


if __name__ == "__main__":
    main()
