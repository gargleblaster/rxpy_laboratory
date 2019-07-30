import config
import rx
from rx import of, from_, create, operators as op
from rx.concurrency import ThreadPoolScheduler
from quotesource import beginStreamingQuotes
import multiprocessing
import logging
import sys

from stock import Stock


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class QuoteObserver():
    def __init__(self):
        logger.debug('QuoteObserver.__init__')

    def requestQuotes(self, tickers):
        logger.debug(f'QuoteObserver.requestQuotes({tickers})')
        self.quoteSubscription = create(lambda o,s: beginStreamingQuotes(tickers, o, s)).pipe(
            op.subscribe_on(config.pool_scheduler),
            op.observe_on(config.pool_scheduler),
            op.do_action(lambda q: logger.debug(f'QO: {q}')),
            op.group_by(lambda q: q['symbol']),
        ).subscribe(
            on_next=self.handleQuote,
            on_error=lambda e: logger.debug(e),
            on_completed=lambda: logger.debug('QuoteObserver subscription completed')
        )

    def handleQuote(self, q):
        logger.debug(f'QuoteObserver.handleQuote(): creating Stock for {q.key}')
        config.stocks[q.key] = Stock(q, q.key)

