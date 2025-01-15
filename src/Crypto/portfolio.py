import robin_stocks.robinhood as r


class Crypto:
    def __init__(self, symbol, bought_price, amount):
        """
        Initialize a stock with a symbol, purchase price, and amount.
        :param symbol: str, the ticker symbol of the stock
        :param bought_price: float, the price at which the stock was purchased
        :param amount: int, number of shares held
        """
        self.symbol = symbol
        self.bought_price = bought_price
        self.amount = amount

    def update_amount(self, new_amount):
        """
        Update the amount of stock held.
        :param new_amount: int, new number of shares
        """
        self.amount = new_amount

    def update_bought_price(self, new_price):
        """
        Update the price at which the stock was bought.
        :param new_price: float, new buy price
        """
        self.bought_price = new_price

    def value(self):
        """
        Calculate the total value of this stock based on the current price.
        :return: float, the total value of the stock held in portfolio
        """
        return self.amount * round(float(r.get_crypto_quote(self.symbol)[0]), 2)

    def __repr__(self):
        return f"Crypto(symbol={self.symbol}, bought_price={self.bought_price}, amount={self.amount})"


class Portfolio:
    def __init__(self, cash):
        """
        Initialize the portfolio with available cash.
        :param cash: float, the amount of cash available to buy crypto
        """
        self.profit = 0.0
        self.cash = cash
        self.crypto = {}  # Dictionary to hold crypto by their symbol (key)

    def buy_stock(self, stock, amount):
        """
        Buy stock and update the portfolio.
        :param stock: Crypto object, the stock to buy
        :param amount: int, the number of shares to buy
        """
        current_price = round(float(r.get_crypto_quote(stock)[0]), 2)
        total_cost = current_price * amount
        if total_cost <= self.cash:
            if stock in self.crypto:
                self.crypto[stock].amount += amount
            else:
                self.crypto[stock] = Crypto(stock, current_price, amount)
            self.cash -= round(total_cost, 2)
            print(f"Bought {amount} shares of {stock} for {total_cost} at {current_price} a share.")
        else:
            print(f"Not enough cash to buy {amount} of {stock}. Current balance is {self.cash}, cost is {total_cost}")

    def sell_stock(self, symbol, amount):
        """
        Sell stock and update the portfolio.
        :param symbol: str, the symbol of the stock to sell
        :param amount: int, the number of shares to sell
        """
        if symbol in self.crypto and self.crypto[symbol].amount >= amount:
            stock = self.crypto[symbol]
            stock.amount -= amount
            current_price = round(float(r.get_crypto_quote(symbol)[0]), 2)
            profit = (current_price * amount) -(round(stock.bought_price * amount,2))
            if profit <= 0:
                print(f"Sold {symbol} for a loss of {profit}")
            else:
                print(f"Sold {symbol} for a gain of {profit}")
            self.cash += round(amount * current_price, 2)
            self.profit += profit
            if stock.amount == 0:
                del self.crypto[symbol]  # Remove the stock if no shares are left
        else:
            print(f"Not enough {symbol} shares to sell.")

    def portfolio_value(self):
        """
        Calculate the total value of the portfolio (cash + value of held crypto).
        :param current_prices: dict, current market prices of all held crypto
        :return: float, the total value of the portfolio
        """
        total_value = self.cash
        for symbol, stock in self.crypto.items():
            total_value += stock.value()
        return total_value

    def __repr__(self):
        return f"Portfolio(profit={self.profit}, cash={self.cash}, crypto={self.crypto})"
