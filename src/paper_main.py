import os
import robin_stocks.robinhood as r
import pprint as p
from algorithms import find_stocks_to_buy
from collections import defaultdict

username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')

r.login(username, password)

account_info = r.load_account_profile()

profit = 0

stocks = find_stocks_to_buy()

# Output the result
p.pprint(stocks)
