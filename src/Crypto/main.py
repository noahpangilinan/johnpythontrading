import os
import robin_cryptos.robinhood as r
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
    if portfolio.cash > amount * float(r.get_crypto_quote(symbol)[0]):
        portfolio.buy_crypto(symbol, amount)
        r.order_buy_crypto_by_price(symbol=symbol, amountInDollars=amount)
        print(portfolio)


def scan_and_buy(portfolio):
    while True:
        cryptos = find_crypto_to_buy()
        # print(f"Found {len(cryptos)} cryptos.")
        for crypto in cryptos:
            # print(f"Scanning {crypto[0]}")
            # if crypto[1] > -1:
            fractionalamount = (2.0 / round(float(r.get_crypto_quote(crypto[0])[0]), 2))
            buy(portfolio, crypto[0], fractionalamount)




def scan_and_sell(portfolio):
    while True:
        for crypto in list(portfolio.cryptos.keys()):
            # print(f"Scanning {crypto}")

            cur_price = round(float(r.get_crypto_quote(crypto)[0]), 2)
            bought_price = portfolio.cryptos[crypto].bought_price
            if cur_price != bought_price:
                print(f"Current price of {crypto}: {cur_price}, bought price: {bought_price}")
            amount = portfolio.cryptos[crypto].amount
            if (bought_price * .98) > cur_price:
                print(f"Stop loss. Selling at 98% Bought at {bought_price}, selling at {cur_price}")
                sell(portfolio, crypto, amount)
                print(portfolio)

            elif (cur_price > bought_price * 1.005) and (cur_price - bought_price >= 0.01):
                sell(portfolio, crypto, amount)
                print(portfolio)

def sell(portfolio, symbol, amount):
    if amount < 0:
        amount = portfolio.cryptos[symbol].value()
    portfolio.sell_crypto(symbol, amount)
    r.order_sell_crypto_by_price(symbol=symbol, amountInDollars=amount)


buyingthread = threading.Thread(target=scan_and_buy, args=(main_portfolio,))
sellingthread = threading.Thread(target=scan_and_sell, args=(main_portfolio,))

buyingthread.start()
sellingthread.start()

# scan_and_buy(main_portfolio)
# Output the result
# p.pprint(cryptos)
