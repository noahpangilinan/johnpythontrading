import robin_stocks.robinhood as r


class Crypto:
    def __init__(self, symbol, bought_price, amount):
        """
        Initialize a crypto with a symbol, purchase price, and amount.
        :param symbol: str, the ticker symbol of the crypto
        :param bought_price: float, the price at which the crypto was purchased
        :param amount: int, number of shares held
        """
        self.symbol = symbol
        self.bought_price = bought_price
        self.highest_price = bought_price
        self.amount = amount

    def update_amount(self, new_amount):
        """
        Update the amount of crypto held.
        :param new_amount: int, new number of shares
        """
        self.amount = new_amount

    def update_bought_price(self, new_price):
        """
        Update the price at which the crypto was bought.
        :param new_price: float, new buy price
        """
        self.bought_price = new_price

    def value(self):
        """
        Calculate the total value of this crypto based on the current price.
        :return: float, the total value of the crypto held in portfolio
        """
        return self.amount * round(float(r.get_crypto_quote(self.symbol)[0]), 2)

    def update_highest_price(self, price):
        self.highest_price = price


    def __repr__(self):
        return f"Crypto(symbol={self.symbol}, bought_price={self.bought_price}, amount={self.amount})"


class Portfolio:
    def __init__(self, cash, crypto = None):
        """
        Initialize the portfolio with available cash.
        :param cash: float, the amount of cash available to buy crypto
        """
        self.profit = 0.0
        self.cash = cash
        self.crypto = crypto if crypto is not None else {}  # Dictionary to hold crypto by their symbol (key)

    def buy_crypto(self, crypto, amount):
        """
        Buy crypto and update the portfolio.
        :param crypto: Crypto object, the crypto to buy
        :param amount: int, the number of shares to buy
        """
        current_price =  round(float(r.get_crypto_quote(crypto)["ask_price"]), 2)
        total_cost = current_price * amount
        if total_cost <= self.cash:
            if crypto in self.crypto:
                self.crypto[crypto].amount += amount
            else:
                self.crypto[crypto] = Crypto(crypto, current_price, amount)
            self.cash -= round(total_cost, 2)
            print(f"Bought {amount} shares of {crypto} for {total_cost} at {current_price} a share.")
        else:
            print(f"Not enough cash to buy {amount} of {crypto}. Current balance is {self.cash}, cost is {total_cost}")

    def sell_crypto(self, symbol, amount):
        """
        Sell crypto and update the portfolio.
        :param symbol: str, the symbol of the crypto to sell
        :param amount: int, the number of shares to sell
        """
        if symbol in self.crypto and self.crypto[symbol].amount >= amount:
            crypto = self.crypto[symbol]
            crypto.amount -= amount
            current_price = round(float(r.get_crypto_quote(symbol)["ask_price"]), 2)
            profit = (current_price * amount) -(round(crypto.bought_price * amount,2))
            if profit <= 0:
                print(f"Sold {symbol} for a loss of {profit}")
            else:
                print(f"Sold {symbol} for a gain of {profit}")
            self.cash += round(amount * current_price, 2)
            self.profit += profit
            if crypto.amount == 0:
                del self.crypto[symbol]  # Remove the crypto if no shares are left
        else:
            print(f"Not enough {symbol} shares to sell.")

    def portfolio_value(self):
        """
        Calculate the total value of the portfolio (cash + value of held crypto).
        :param current_prices: dict, current market prices of all held crypto
        :return: float, the total value of the portfolio
        """
        total_value = self.cash
        for symbol, crypto in self.crypto.items():
            total_value += crypto.value()
        return total_value

    def add_crypto(self, crypto, amount, bought_price):
        if crypto in self.crypto:
            self.crypto[crypto].amount += amount
        else:
            self.crypto[crypto] = Crypto(crypto, bought_price, amount)

    def set_cash(self, cash):
        self.cash = cash

    def __repr__(self):
        return f"Portfolio(profit={self.profit}, cash={self.cash}, crypto={self.crypto})"
