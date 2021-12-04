from foe_bot.request import Request
from persistent.account import Account


def main():
    req, ctn = Request()
    account = Account()
    for item in ctn:
        account.populate(**item)

    print('ok')
