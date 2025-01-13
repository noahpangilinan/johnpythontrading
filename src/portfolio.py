class Stock:
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

    def value(self, current_price):
        """
        Calculate the total value of this stock based on the current price.
        :param current_price: float, the current market price of the stock
        :return: float, the total value of the stock held in portfolio
        """
        return self.amount * current_price

    def __repr__(self):
        return f"Stock(symbol={self.symbol}, bought_price={self.bought_price}, amount={self.amount})"


class Portfolio:
    def __init__(self, cash):
        """
        Initialize the portfolio with available cash.
        :param cash: float, the amount of cash available to buy stocks
        """
        self.cash = cash
        self.stocks = {}  # Dictionary to hold stocks by their symbol (key)

    def buy_stock(self, stock, amount):
        """
        Buy stock and update the portfolio.
        :param stock: Stock object, the stock to buy
        :param amount: int, the number of shares to buy
        """
        total_cost = stock.bought_price * amount
        if total_cost <= self.cash:
            if stock.symbol in self.stocks:
                self.stocks[stock.symbol].amount += amount
            else:
                self.stocks[stock.symbol] = Stock(stock.symbol, stock.bought_price, amount)
            self.cash -= total_cost
        else:
            print(f"Not enough cash to buy {amount} of {stock.symbol}")

    def sell_stock(self, symbol, amount, current_price):
        """
        Sell stock and update the portfolio.
        :param symbol: str, the symbol of the stock to sell
        :param amount: int, the number of shares to sell
        :param current_price: float, the current market price of the stock
        """
        if symbol in self.stocks and self.stocks[symbol].amount >= amount:
            stock = self.stocks[symbol]
            stock.amount -= amount
            self.cash += amount * current_price
            if stock.amount == 0:
                del self.stocks[symbol]  # Remove the stock if no shares are left
        else:
            print(f"Not enough {symbol} shares to sell.")

    def portfolio_value(self, current_prices):
        """
        Calculate the total value of the portfolio (cash + value of held stocks).
        :param current_prices: dict, current market prices of all held stocks
        :return: float, the total value of the portfolio
        """
        total_value = self.cash
        for symbol, stock in self.stocks.items():
            total_value += stock.value(current_prices.get(symbol, 0))
        return total_value

    def __repr__(self):
        return f"Portfolio(cash={self.cash}, stocks={self.stocks})"
