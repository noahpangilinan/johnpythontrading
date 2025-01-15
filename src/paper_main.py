import os
import robin_stocks.robinhood as r
import pprint as p
import threading
from dotenv import load_dotenv
from algorithms import find_stocks_to_buy
from portfolio import Portfolio, Stock

load_dotenv()
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

r.login(username, password)

account_info = r.load_account_profile()
p.pprint(account_info)
main_portfolio = Portfolio(cash=round(float(account_info['portfolio_cash']),2))

def buy(portfolio, symbol, amount):
    if portfolio.cash > amount:
        portfolio.buy_stock(symbol, amount)
        print(portfolio)


def scan_and_buy(portfolio):
    while True:
        stocks = find_stocks_to_buy()
        # print(f"Found {len(stocks)} stocks.")
        for stock in stocks:
            # print(f"Scanning {stock[0]}")
            if stock[1] > 0:
                fractionalamount = (1.0 / round(float(r.get_latest_price(stock[0])[0]), 2))
                buy(portfolio, stock[0], fractionalamount)




def scan_and_sell(portfolio):
    while True:
        for stock in list(portfolio.stocks.keys()):
            # print(f"Scanning {stock}")

            cur_price = round(float(r.get_latest_price(stock)[0]), 2)
            bought_price = portfolio.stocks[stock].bought_price
            amount = portfolio.stocks[stock].amount
            if (bought_price * .98) > cur_price:
                print(f"Stop loss. Selling at 98% Bought at {bought_price}, selling at {cur_price}")
                sell(portfolio, stock, amount)
                print(portfolio)

            elif (cur_price > bought_price * 1.01) and (cur_price - bought_price >= 0.01):
                sell(portfolio, stock, amount)
                print(portfolio)

def sell(portfolio, symbol, amount):
    if amount < 0:
        amount = portfolio.stocks[symbol].value()
    portfolio.sell_stock(symbol, amount)


buyingthread = threading.Thread(target=scan_and_buy, args=(main_portfolio,))
sellingthread = threading.Thread(target=scan_and_sell, args=(main_portfolio,))

buyingthread.start()
sellingthread.start()

# scan_and_buy(main_portfolio)
# Output the result
# p.pprint(stocks)
