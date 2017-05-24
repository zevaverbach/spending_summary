import os
from typing import List

from twilio.rest import Client as TwilioClient

twilio_client = TwilioClient(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))


def send_summary(transactions: List[dict]) -> None:
    total_spent = sum(transaction['amount'] for transaction in transactions)
    message = f'You spent ${total_spent} yesterday. 💸'
    twilio_client.api.account.messages.create(to=os.getenv('MY_CELL'), from_=os.getenv('MY_TWILIO_NUM'), body=message)


if __name__ == "__main__":
    send_summary(get_yesterdays())
