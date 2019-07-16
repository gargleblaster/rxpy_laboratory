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
        self.market = create(market)
        self.entryTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.do_action(lambda x: print(f'entryTrigger {x}')),
            op.filter(lambda q: self.position == 0 and q['ask'] >= self.entryPrice),
            op.subscribe_on(pool_scheduler)
        )
        self.targetTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.do_action(lambda x: print(f'targetTrigger {x}')),
            op.filter(lambda q: self.position > 0 and q['bid'] >= self.targetPrice),
            op.subscribe_on(pool_scheduler)
        )
        self.stopTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.do_action(lambda x: print(f'stopTrigger {x}')),
            op.filter(lambda q: self.position > 0 and q['bid'] <= self.stopPrice),
            op.subscribe_on(pool_scheduler)
        )
        self.subscriptions = {}


    def setupTrade(self, qty, entry, target, stop):
        self.quantity = qty
        self.entryPrice = entry
        self.targetPrice = target
        self.stopPrice = stop

        self.subscriptions['entryTrigger'] = self.entryTrigger.subscribe(
            lambda x: self.openPosition(),
            scheduler=pool_scheduler
        )


    def openPosition(self):
        print(f'bought {self.quantity} {self.ticker}')
        self.position = self.quantity

        self.subscriptions['targetTrigger'] = self.targetTrigger.subscribe(
            lambda x: self.closePosition(),
            scheduler=pool_scheduler
        )

        self.subscriptions['stopTrigger'] = self.stopTrigger.subscribe(
            lambda x: self.closePosition(),
            scheduler=pool_scheduler
        )

    def closePosition(self):
        print(f'sold {self.quantity} {self.ticker}')
        self.position = 0


    def dispose(self):
        print('dispose')
        if 'entryTrigger' in self.subscriptions:
            self.subscriptions['entryTrigger'].dispose()
            del self.subscriptions['entryTrigger']
        if 'targetTrigger' in self.subscriptions:
            self.subscriptions['targetTrigger'].dispose()
            del self.subscriptions['targetTrigger']
        if 'stopTrigger' in self.subscriptions:
            self.subscriptions['stopTrigger'].dispose()
            del self.subscriptions['stopTrigger']
