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
        self.quotesource = create(market)
        self.quotesource.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.subscribe_on(pool_scheduler)
        ).subscribe(
            on_next = self.on_next
        )

    def setupTrade(self, qty, entry, target, stop):
        self.quantity = qty
        self.entryPrice = entry
        self.targetPrice = target
        self.stopPrice = stop

    def on_next(self, val):
        print(f'on_next {val}')
        self.quotesource.pipe(
            op.subscribe_on(pool_scheduler),
            self.entryPriceHit()
        ).subscribe(on_next = lambda v: print('.'))

    def on_completed(self):
        print(f'on_completed')

    def on_error(self, error):
        print(f'on_error {error}')

    def openPosition(self):
        print(f'bought {self.quantity} {self.ticker}')
        self.position = self.quantity

    def entryPriceHit(self):
        return rx.pipe(
            op.filter(lambda q: self.position == 0 and q['ask'] >= self.entryPrice)
        ).subscribe(self.openPosition)
