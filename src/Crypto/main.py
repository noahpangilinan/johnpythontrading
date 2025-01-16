import os
import time

import robin_stocks.robinhood as r
import pprint as p
import threading
from dotenv import load_dotenv
from algorithms import find_crypto_to_buy
from portfolio import Portfolio, Crypto

load_dotenv()
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

r.login(username, password)

account_info = r.load_account_profile()
p.pprint(account_info)
main_portfolio = Portfolio(cash=round(float(account_info['portfolio_cash']),2))

def buy(portfolio, symbol, amount):
    if portfolio.cash > amount * round(float(r.get_crypto_quote(symbol)["ask_price"]), 2):
        amount = round(amount, 4)
        status = r.order_buy_crypto_by_quantity(symbol=symbol, quantity=round(amount, 4))
        if isinstance(status['quantity'], str):  # Replace 'status' with the actual field name from the response
            print("Order placed successfully.")
            portfolio.buy_crypto(symbol, amount)
            print(portfolio)

        elif isinstance(status['quantity'], list):   # Example error checking, adapt based on actual response structure
            print(f"Error placing order: {status}")
        else:
            print("Unknown result:", status)

        print(status)


def scan_and_buy(portfolio):
    while True:
        crypto = find_crypto_to_buy()
        # print(f"Found {len(crypto)} crypto.")
        for cryptos in crypto:
            time.sleep(1)

            # print(f"Scanning {crypto[0]}")
            # if crypto[1] > -1:
            if not None:
                if not round(float(r.get_crypto_quote(cryptos[0])["ask_price"])) == 0:
                    fractionalamount = (5.0 / round(float(r.get_crypto_quote(cryptos[0])["ask_price"]), 2))
                    buy(portfolio, cryptos[0], fractionalamount)




def scan_and_sell(portfolio):
    while True:
        for crypto in list(portfolio.crypto.keys()):
            time.sleep(1)

            # print(f"Scanning {crypto}")

            cur_price = round(float(r.get_crypto_quote(crypto)["ask_price"]), 2)
            bought_price = portfolio.crypto[crypto].bought_price
            highest_price = portfolio.crypto[crypto].highest_price
            # if cur_price != bought_price:
            #     print(f"Current price of {crypto}: {cur_price}, bought price: {bought_price}")
            amount = portfolio.crypto[crypto].amount
            print(
                f"Current price of {crypto} is {cur_price}, bought for {bought_price}. Total profit is {amount * (cur_price - bought_price) - max(0.02, amount * bought_price * 0.0126)}. Highest price is {highest_price} ")

            if (bought_price * .98) > cur_price:
                print(f"Stop loss. Selling at 98% Bought at {bought_price}, selling at {cur_price}")
                sell(portfolio, crypto, amount)
                print(portfolio)

            elif cur_price > bought_price:
                if cur_price > highest_price:
                    portfolio.crypto[crypto].update_highest_price(cur_price)
                elif cur_price < (highest_price * 0.99) and (amount * (cur_price - bought_price) - (max(0.01, amount * bought_price * 0.0063) + max(0.01, amount * cur_price * 0.0063)) > 0) :
                    sell(portfolio, crypto, amount)
                    print(portfolio)

def sell(portfolio, symbol, amount):
    if amount < 0:
        amount = portfolio.crypto[symbol].value()
    portfolio.sell_crypto(symbol, amount)
    r.order_sell_crypto_by_quantity(symbol=symbol, quantity=amount)


buyingthread = threading.Thread(target=scan_and_buy, args=(main_portfolio,))
sellingthread = threading.Thread(target=scan_and_sell, args=(main_portfolio,))

buyingthread.start()
sellingthread.start()

# scan_and_buy(main_portfolio)
# Output the result
# p.pprint(crypto)
