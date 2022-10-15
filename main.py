import praw
import alpaca_trade_api as tradeapi
from textblob import TextBlob
import time
import json
import csv
import re

CLIENT_ID = "MY_REDDIT_CLIENT_ID"
CLIENT_SECRET = "MY_REDDIT_CLIENT_SECRET"

ALPACA_API_KEY = "ALPACA_API_KEY"
ALPACA_SECRET_KEY = "ALPACA_SECRET_KEY_VALUE"

reddit_api_client = praw.Reddit(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    user_agent = "our trading bot | by /u/your_reddit_username"
)

api = tradeapi.REST(
    ALPACA_API_KEY, 
    ALPACA_SECRET_KEY, 
    "https://paper-api.alpaca.markets"
)

# This function returns the most recent "What are your moves" thread
def get_weekly_most_recent_link():
    user = reddit_api_client.redditor("OPINION_IS_UNPOPULAR")
    for post in user.submissions.new(limit=None):
        if "What Are Your Moves Tomorrow" in post.title:
            return post

def extract_all_comments_from_post(post):
    post.comments.replace_more()
    return [comment.body for comment in post.comments]

STOCK_LIST = set()

with open("stocks.csv", "r") as f:
    reader = csv.reader(f)
    for val in list(reader)[1:]:
        STOCK_LIST.add(val[0])

def extract_stock_from_comment(comment):
    return set(re.findall("\w+", comment)).intersection(STOCK_LIST)

def get_ticket_sentiment_mapping():
    mapping = {}

    post = get_weekly_most_recent_link()
    for comment in extract_all_comments_from_post(post):
        stocks_mentioned = extract_stock_from_comment(comment)
        for ticker in stocks_mentioned:
            if ticker not in mapping:
                mapping[ticker] = []
            mapping[ticker].append(TextBlob(comment).polarity)
    return {stock: sum(values) / len(values) for stock, values in mapping.items()}

def make_trade(ticker, short=False):
    if short == True:
        api.submit_order(
            symbol=ticker,
            qty=1,
            type='limit',
            side='sell',
            limit_price='999',
            time_in_force='day',
            extended_hours=True
        )
        print("Shorted {}".format(ticker))
    else:
        api.submit_order(
            symbol=ticker,
            qty=1,
            type='limit',
            side='buy',
            limit_price='999',
            time_in_force='day',
            extended_hours=True
        )
        print("Purchased {}".format(ticker))


for stock, sentiment in get_ticket_sentiment_mapping().items():
    if sentiment > 0:
        make_trade(stock, short=True)
    elif sentiment < 0:
        make_trade(stock)




