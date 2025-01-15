import os
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
    if portfolio.cash > amount * float(r.get_crypto_quote(symbol)[0]):
        portfolio.buy_stock(symbol, amount)
        # r.order_buy_fractional_by_price(symbol=symbol, amountInDollars=amount)
        print(portfolio)


def scan_and_buy(portfolio):
    while True:
        crypto = find_crypto_to_buy()
        # print(f"Found {len(crypto)} crypto.")
        for stock in crypto:
            # print(f"Scanning {stock[0]}")
            # if stock[1] > -1:
            print(sto)
            fractionalamount = (2.0 / round(float(r.get_crypto_quote(stock[0])["bid_price"]), 2))
            buy(portfolio, stock[0], fractionalamount)




def scan_and_sell(portfolio):
    while True:
        for stock in list(portfolio.crypto.keys()):
            # print(f"Scanning {stock}")

            cur_price = round(float(r.get_crypto_quote(stock)[0]), 2)
            bought_price = portfolio.crypto[stock].bought_price
            if cur_price != bought_price:
                print(f"Current price of {stock}: {cur_price}, bought price: {bought_price}")
            amount = portfolio.crypto[stock].amount
            if (bought_price * .98) > cur_price:
                print(f"Stop loss. Selling at 98% Bought at {bought_price}, selling at {cur_price}")
                sell(portfolio, stock, amount)
                print(portfolio)

            elif (cur_price > bought_price * 1.005) and (cur_price - bought_price >= 0.01):
                sell(portfolio, stock, amount)
                print(portfolio)

def sell(portfolio, symbol, amount):
    if amount < 0:
        amount = portfolio.crypto[symbol].value()
    portfolio.sell_stock(symbol, amount)
    # r.order_sell_fractional_by_price(symbol=symbol, amountInDollars=amount)


buyingthread = threading.Thread(target=scan_and_buy, args=(main_portfolio,))
sellingthread = threading.Thread(target=scan_and_sell, args=(main_portfolio,))

buyingthread.start()
sellingthread.start()

# scan_and_buy(main_portfolio)
# Output the result
# p.pprint(crypto)
