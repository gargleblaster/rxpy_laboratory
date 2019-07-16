import rx
from rx import of, create, operators as op
from rx.concurrency import ThreadPoolScheduler
import multiprocessing

thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(thread_count)

class Trade:
    def __init__(self, ticker, market):
        self.ticker = ticker
        self.position = 0
        self.quantity = -1
        self.entryPrice = -1
        self.targetPrice = -1
        self.stopPrice = -1
        self.quotesource = create(market).pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.do_action(print),
            op.filter(lambda q: self.position == 0 and q['ask'] >= self.entryPrice),
            op.subscribe_on(pool_scheduler)
        )
        self.subscription = None

    def setupTrade(self, qty, entry, target, stop):
        self.quantity = qty
        self.entryPrice = entry
        self.targetPrice = target
        self.stopPrice = stop

        self.subscription = self.quotesource.subscribe(
            lambda x: self.openPosition(),
            scheduler=pool_scheduler
        )


    def openPosition(self):
        print(f'bought {self.quantity} {self.ticker}')
        self.position = self.quantity


    def dispose(self):
        if self.subscription:
            self.subscription.dispose()
            self.subscription = None
