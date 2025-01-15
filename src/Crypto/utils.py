from pathlib import Path

import robin_stocks.robinhood as r
import pandas as pd
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