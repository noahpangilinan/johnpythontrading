import base64
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import robin_stocks.robinhood as r
import pprint as p
import threading
from dotenv import load_dotenv
from algorithms import find_crypto_to_buy
from portfolio import Portfolio, Crypto
from utils import load_portfolio

hourly_profit = 0
hourly_trades = []
hourly_sold = 0
# Email details

def start_main_loop():
    load_dotenv()
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    emailusername = os.getenv('EMAIL_USERNAME')
    emailpassword = os.getenv('EMAIL_PASSWORD')
    api_key = os.getenv('API_KEY')
    r.login(username, password)

    account_info = r.load_account_profile()
    p.pprint(account_info)
    main_portfolio = load_portfolio()
    buyingthread = threading.Thread(target=scan_and_buy, args=(main_portfolio,))
    sellingthread = threading.Thread(target=scan_and_sell, args=(main_portfolio,))

    buyingthread.start()
    sellingthread.start()

def buy(portfolio, symbol, amount):
    global hourly_trades
    global hourly_sold
    if portfolio.cash > amount * round(float(r.get_crypto_quote(symbol)["ask_price"]), 2):
        amount = round(amount, 4)
        status = r.order_buy_crypto_by_quantity(symbol=symbol, quantity=round(amount, 3))
        if status is None or 'quantity' not in status.keys():
            print("Unknown result:", status)
            print(portfolio)

        elif isinstance(status['quantity'], str):  # Replace 'status' with the actual field name from the response
            print("Order placed successfully.")
            portfolio.buy_crypto(symbol, amount)
            print(portfolio)
            hourly_trades += [f"Bought {amount} of {symbol} for ${amount * round(float(r.get_crypto_quote(symbol)["ask_price"]), 2)}"]
            hourly_sold += 1
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



# def send_email(portfolio):
#
#     sender_email = emailusername
#     receiver_email = emailusername
#     subject = "Hourly Profits"
#
#
#
#     try:
#         msg = MIMEText(body)
#         msg['Subject'] = subject
#         msg['From'] = emailusername
#         msg['To'] = receiver_email
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
#             smtp_server.login(emailusername, password)
#             smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
#
#
#         print("Email sent successfully!")
#         hourly_profit = 0
#         hourly_trades = []
#         hourly_sold = 0
#     except Exception as e:
#         print(f"Failed to send email: {e}")



def send_email(portfolio):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  """
  global hourly_profit
  global hourly_trades
  global hourly_sold

  # Looking to send emails in production? Check out our Email API/SMTP product!
  import smtplib
  sender = "hello@noahpangilinan.com"
  receiver = "A Test User <johnpythontrading@gmail.com>"
  modified_hourly_trades = [f"\t{string}\n" for string in hourly_trades]

  msg = MIMEText(f'You completed {len(hourly_trades)} for a total profit of ${hourly_profit}.'
                 f'Trades: {modified_hourly_trades}')
  msg['From'] = sender  # Ensure this matches the sender's email domain
  msg['To'] = receiver
  msg['Subject'] = "Hourly Report"
  with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("api", '0675362267e0a1f50123a3c04f6471b5')
    server.sendmail(sender, receiver, msg.as_string())
  hourly_sold = 0
  hourly_trades = []
  hourly_profit = 0

def scan_and_sell(portfolio):
    last_sent_time = -3600
    global hourly_profit
    global hourly_trades
    global hourly_sold
    while True:
        # Send the email
        current_time = time.time()
        if current_time - last_sent_time >= 3600:
            send_email(portfolio)
            last_sent_time = current_time  # Update the last sent time


        for crypto in list(portfolio.crypto.keys()):
            time.sleep(1)

            # print(f"Scanning {crypto}")

            cur_price = round(float(r.get_crypto_quote(crypto)["ask_price"]), 2)
            bought_price = portfolio.crypto[crypto].bought_price
            highest_price = portfolio.crypto[crypto].highest_price
            # if cur_price != bought_price:
            #     print(f"Current price of {crypto}: {cur_price}, bought price: {bought_price}")
            amount = portfolio.crypto[crypto].amount
            profit =  amount * (cur_price - bought_price) - max(0.02, amount * bought_price * 0.0126)
            print(
                f"Current price of {crypto} is {cur_price}, bought for {bought_price}. Total profit is {profit}. Highest price is {highest_price} ")

            if (bought_price * .98) > cur_price:
                print(f"Stop loss. Selling at 98% Bought at {bought_price}, selling at {cur_price}")
                sell(portfolio, crypto, amount)
                print(portfolio)
                hourly_profit += profit
                hourly_trades += f"Sold {amount} of {crypto} for a loss of ${profit}"
                hourly_sold += 1
            elif cur_price > bought_price:
                if cur_price > highest_price:
                    portfolio.crypto[crypto].update_highest_price(cur_price)
                elif cur_price < (highest_price * 0.999) and (amount * (cur_price - bought_price) - (max(0.01, amount * bought_price * 0.0063) + max(0.01, amount * cur_price * 0.0063)) > 0) :
                    sell(portfolio, crypto, amount)
                    print(portfolio)
                    hourly_profit += profit
                    hourly_trades += [f"Sold {amount} of {crypto} for a gain of ${profit}"]
                    hourly_sold += 1


def sell(portfolio, symbol, amount):
    if amount < 0:
        amount = portfolio.crypto[symbol].value()
    portfolio.sell_crypto(symbol, amount)
    status = r.order_sell_crypto_by_quantity(symbol=symbol, quantity=amount)
    if status is None or 'quantity' not in status.keys():
        print("Unknown result:", status)
        print(portfolio)

    elif isinstance(status['quantity'], str):  # Replace 'status' with the actual field name from the response
        print("Sold successfully.")
        portfolio.sell_crypto(symbol, amount)
        print(portfolio)
        account_info = r.load_account_profile()
        portfolio.set_cash(round(float(account_info['buying_power']), 2))

    elif isinstance(status['quantity'], list):   # Example error checking, adapt based on actual response structure
        print(f"Error placing order: {status}")
    else:
        print("Unknown result:", status)


def inifiniteloop():
    try:
        start_main_loop()
    except:
        print("Failed. Starting again.")
        inifiniteloop()

inifiniteloop()
# scan_and_buy(main_portfolio)
# Output the result
# p.pprint(crypto)
