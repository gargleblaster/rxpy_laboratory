import rx
from rx import of, create, operators as op
from rx.concurrency import ThreadPoolScheduler
import multiprocessing

thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(thread_count)

class Trade:
    def __init__(self, ticker, market):
        self.ticker = ticker
        quotesource = create(market)
        quotesource.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.subscribe_on(pool_scheduler)
        ).subscribe(
            on_next = self.on_next
        )

    def on_next(self, val):
        print(f'on_next {val}')

    def on_completed(self):
        print(f'on_completed')

    def on_error(self, error):
        print(f'on_error {error}')
