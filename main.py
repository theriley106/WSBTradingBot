import praw
import json
import time
import csv
import re
import * from keys

STOCK_LIST = set()

with open("stocks.csv", "r") as f:
    reader = csv.reader(f)
    for val in list(reader)[1:]:
        STOCK_LIST.add(val[0])

reddit_api_client = praw.Reddit(
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
    user_agent="our trading bot"
)

def get_weekly_most_recent_link():
    user = reddit_api_client.redditor('OPINION_IS_UNPOPULAR')
    for post in user.submissions.new(limit=None):
        if "What Are Your Moves Tomorrow" in post.title:
            return post

def extract_all_comments_from_post(post):
    vals = []
    for comment in post.comments:
        try:
            vals.append(comment.body)
        except:
            break
    return vals
    post.comments.replace_more()
    return [comment.body for comment in post.comments]

def extract_stock_from_comment(comment):
    return set(re.findall("\w+", comment)).intersection(STOCK_LIST)

def extract_top_n_tickers(n):
    counter = {}

    post = get_weekly_most_recent_link()
    for comment in extract_all_comments_from_post(post):
        stocks_mentioned = extract_stock_from_comment(comment)
        for ticker in stocks_mentioned:
            if ticker not in counter:
                counter[ticker] = 0
            counter[ticker] += 1
    return sorted(list(counter.keys()), key=lambda k: counter[k], reverse=True)[:n]

import alpaca_trade_api as tradeapi
api = tradeapi.REST(ALPACA_API_KEY,
APACA_SECRET_KEY,"https://paper-api.alpaca.markets")
for stock in extract_top_n_tickers(5):
    try:
        order = api.submit_order(
            symbol=stock,
            qty=15,
            type='limit',
            side='sell',
            limit_price='999',
            time_in_force='day',
            extended_hours=True,
        )
    except Exception as exp:
        print(exp)



