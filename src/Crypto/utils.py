import os
from pathlib import Path
import pprint as p
import robin_stocks.robinhood as r
import pandas as pd
from dotenv import load_dotenv

from src.Crypto.portfolio import Portfolio


def write_all_symbols_to_file(filename, output_file):
    listings = pd.read_csv(filename, header=0)
    symbols = listings["Symbol"].drop_duplicates()
    symbols.to_csv(output_file)


def get_all_symbols():
    symbols = pd.read_csv(Path("all_symbols.csv"), header=0)
    return list(symbols["Symbol"])

def get_all_penny_symbols():
    symbols = pd.read_csv(Path("listed_penny.csv"), header=0)
    return list(symbols["Symbol"])


def load_portfolio():
    load_dotenv()
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')

    r.login(username, password)

    account_info = r.load_account_profile()
    # p.pprint(account_info)
    main_portfolio = Portfolio(cash=round(float(account_info['buying_power']), 2))

    allcrypto = r.get_crypto_positions()
    for crypto in allcrypto:
        if float(crypto['quantity']) > 0:
            bought_price = get_price_at_time(crypto['currency']['code'], crypto['created_at'][:19])
            main_portfolio.add_crypto(crypto['currency']['code'], float(crypto['quantity']), bought_price)
    return main_portfolio



def get_price_at_time(symbol, timestamp):
    import requests
    from datetime import datetime

    kraken_symbol_map = {
        "ETH": "XETHZUSD",  # Ethereum to USD
        "DOGE": "XDGUSD",  # Dogecoin to USD
        "LTC": "XLTCZUSD",  # Litecoin to USD
        "SHIB": "SHIBUSD",  # Shiba Inu to USD
        "AAVE": "AAVEUSD",  # Aave to USD
        "AVAX": "AVAXUSD",  # Avalanche to USD
        "BCH": "BCHUSD",  # Bitcoin Cash to USD
        "BONK": "BONKUSD",  # Bonk to USD
        "ADA": "ADAUSD",  # Cardano to USD
        "LINK": "LINKUSD",  # Chainlink to USD
        "COMP": "COMPUSD",  # Compound to USD
        "WIF": "WIFUSD",  # Wifecoin to USD (check for availability on Kraken)
        "ETC": "XETCZUSD",  # Ethereum Classic to USD
        "PEPE": "PEPEUSD",  # Pepe Coin to USD (check for availability on Kraken)
        "SOL": "SOLUSD",  # Solana to USD
        "XLM": "XLMUSD",  # Stellar Lumens to USD
        "XTZ": "XTZUSD",  # Tezos to USD
        "UNI": "UNIUSD",  # Uniswap to USD
        "XRP": "XRPUSD"  # Ripple to USD
    }

    # Function to get Kraken historical OHLC data
    def get_kraken_ohlc(pair, interval, since=None):
        url = "https://api.kraken.com/0/public/OHLC"

        # Set the parameters for the request
        params = {
            "pair": pair,  # Cryptocurrency pair, e.g., XBTUSD for Bitcoin to USD
            "interval": interval,  # Time interval (e.g., 1440 for daily data)
        }

        if since:
            params["since"] = since

        # Send the request to Kraken API
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # print(data['result'].keys())
            if "result" in data:
                return data["result"][pair]  # Return the OHLC data
            else:
                print("Error: No data found.")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None

    # Specify the trading pair, interval, and optional 'since' timestamp
    pair = kraken_symbol_map[symbol]
    interval = 1440  # 1440 minutes = 1 day

    date_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    unix_timestamp = int(date_object.timestamp())  # Convert to Unix timestamp

    # Fetch the historical OHLC data
    ohlc_data = get_kraken_ohlc(pair, interval, since=unix_timestamp)
    # Display the data
    if ohlc_data:
        for candle in ohlc_data:
            open_price = candle[1]
            high_price = candle[2]
            low_price = candle[3]
            close_price = candle[4]
            volume = candle[6]
            secslope = (float(close_price) - float(open_price)) / 60
            price = float(open_price) + (secslope * date_object.second)
            return(price)

