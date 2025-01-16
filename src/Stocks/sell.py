import os

import robin_stocks.robinhood as r
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')
r.login(username, password)

positions = r.get_open_stock_positions()
print(positions)

for position in positions:
    symbol = position['symbol']  # Stock symbol (e.g., 'AAPL')
    quantity = float(position['quantity'])  # Quantity of the stock you own

    if quantity > 0:  # Only sell if you own some shares
        print(f"Selling {quantity} shares of {symbol}")
        # Sell all shares (specifying the order type and price; market order will be used here)
        r.order_sell_fractional_by_quantity(symbol, quantity)
        print(f"Successfully sold {quantity} shares of {symbol}")
    else:
        print(f"No shares to sell for {symbol}")