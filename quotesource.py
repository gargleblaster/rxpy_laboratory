from rx import of, operators as op
from time import sleep
import random
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


stocks = [
    {'symbol': 'AAPL',  'bid':  199.0, 'ask':  199.25},
    {'symbol': 'AMZN',  'bid': 1999.0, 'ask': 1999.5},
    {'symbol': 'GOOGL', 'bid': 1199.0, 'ask': 1199.25},
    {'symbol': 'FB',    'bid':  199.0, 'ask':  199.25},
    {'symbol': 'NFLX',  'bid':  375.0, 'ask':  375.25},
]

def beginStreamingQuotes(tickers, observer, scheduler):
    logger.debug('beginStreamingQuotes')
    while True:
        sleep(random.uniform(0.01, 0.10))
        stock = stocks[random.randrange(0, len(stocks))]
        biddelta = random.uniform(0.01, 0.0001*stock['bid'])
        spread = stock['ask'] - stock['bid']
        spreaddelta = random.uniform(-0.05, 0.05)
        updown = random.randrange(0, 2)
        #print(f'updown {updown} biddelta {biddelta:4.2f} spread {spread:4.2f} spreaddelta {spreaddelta:4.2f}')
        if updown:
            bid = stock['bid'] + biddelta
        else:
            bid = stock['bid'] - biddelta

        ask = bid + spread + spreaddelta
        if ask <= bid:
            ask = bid + random.uniform(0.01, 0.10)

        stock['bid'] = bid
        stock['ask'] = ask

        observer.on_next(stock)
