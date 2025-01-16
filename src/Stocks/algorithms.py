"""
All calculations that determine buying, and selling.
"""
from collections import defaultdict
from utils import get_all_symbols, get_all_penny_symbols
import robin_stocks.robinhood as r
from numpy.ma.core import negative

positive_keywords = [
"Growth", "Surge", "Profit", "Revenue", "Earnings", "Record", "Beating", "Exceeding", "Surpassing", "Booming", "Strength", "Increase", "Surplus", "Expansion", "Rise", "Acquisition", "Partnership", "Merger", "Launch", "Innovation", "Entry", "Alliance", "Deal", "Breakthrough", "Approval", "Milestone", "Award", "Investment", "Funding", "Recognition", "Buyback", "Restructuring", "Dividend", "Optimism", "Confidence", "Bullish", "Positive", "Sentiment", "Uptrend", "Investor", "Support", "Excitement", "Momentum", "Recovery", "Boom", "Rebound", "Demand", "Leader", "Dominance", "Rising", "Success", "Outperformance", "Advancement", "Achievement", "Outlook", "Performance", "Upward", "Rally", "Gain", "Upgrade", "Strengthening",
]
negative_keywords = [
"Decline", "Drop", "Loss", "Fall", "Decrease", "Miss", "Underperform", "Disappointing", "Diminish", "Weakness", "Downturn", "Struggling", "Recession", "Slump", "Fail", "Lagging", "Underwhelming", "Stagnation", "Shrinking", "Negative", "Deficit", "Plunge", "Setback", "Disruption", "Layoff", "Resignation", "Cutback", "Bankruptcy", "Default", "Warning", "Losses", "Reversal", "Downgrade", "Failure", "Weak", "Pressure", "Threat", "Risk", "Instability", "Contracting", "Misstep", "Investigation", "Fired", "Crisis", "Slowing", "Declining", "Uncertainty", "Turbulence", "Loss-making", "Lackluster", "Cut", "Retract", "Controversy", "Dispute", "Scandal",
]

def find_stocks_to_buy():
    positive_stocks = []

    for symbol in get_all_symbols():
        for story in r.get_news(symbol):
            net_score = 0
            for word in positive_keywords:
                if word in story['title']:
                    net_score += 1
            for word in negative_keywords:
                if word in story['title']:
                    net_score -= 1
            if net_score > 0:
                # print(symbol, story['title'], net_score)
                positive_stocks.append((symbol, net_score))
            print((symbol, net_score))
    company_counts = defaultdict(int)

    # Iterate over the data and sum the values
    for company, count in positive_stocks:
        company_counts[company] += count

    # Convert the dictionary back to a list of tuples
    positive_stocks = sorted([(company, total_count) for company, total_count in company_counts.items()], key=lambda x: x[1],
                    reverse=True)

    return positive_stocks



def find_penny_stocks_to_buy():
    positive_stocks = []

    for symbol in get_all_penny_symbols():
        # print(symbol)
        for story in r.get_news(symbol):
            net_score = 0
            for word in positive_keywords:
                if word in story['title']:
                    net_score += 1
            for word in negative_keywords:
                if word in story['title']:
                    net_score -= 1
            # if net_score >= 0:
            #     # print(symbol, story['title'], net_score)
            positive_stocks.append((symbol, net_score))
    company_counts = defaultdict(int)

    # Iterate over the data and sum the values
    for company, count in positive_stocks:
        company_counts[company] += count

    # Convert the dictionary back to a list of tuples
    positive_stocks = sorted([(company, total_count) for company, total_count in company_counts.items()], key=lambda x: x[1],
                    reverse=True)

    return positive_stocks
