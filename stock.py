import rx
from rx import of, from_, create, operators as op
import config

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Stock:
    def __init__(self, observer, symbol):
        logger.debug(f'Stock.__init__({symbol})')
        self.observer = observer
        self.symbol = symbol
        self.price = ()
        self.stockSubscription = from_(self.observer).pipe(
            op.subscribe_on(config.pool_scheduler),
            op.observe_on(config.pool_scheduler),
            op.do_action(lambda s: logger.debug(f'STK: {s}')),
        ).subscribe(
            on_next=self.handleQuote,
            on_error=lambda e: logger.debug(e),
            on_completed=lambda: logger.debug('Stock subscription completed')
        )

    def handleQuote(self, q):
        logger.debug(f'Stock.handleQuote({q}')
