from __init__ import plaid_client


def get_banks_by_name(bank_name):
    bank = plaid_client.Institutions.search(bank_name)
    return bank['institutions']


def bank_can_get_transactions(bank):
    return 'transactions' in bank['products']

#too_big_to_fail = ['Bank of America', 'Wells Fargo', 'Chase', 'Citi']
too_big_to_fail = ['Vermont Federal Credit Union', 'American Express', 'Citi']
# I only keep my money in banks that are too big to fail.  If you can't beat 'em...

bank_dict = {}

for bank_name in too_big_to_fail:
    banks = get_banks_by_name(bank_name)
    if len(banks) > 0:
        bank_dict[bank_name] = banks[0]['institution_id']
