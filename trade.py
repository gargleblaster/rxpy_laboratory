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
        self.monitor = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            #op.do_action(print),
            op.subscribe_on(pool_scheduler)
        )
        self.entryTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.filter(lambda q: self.position == 0 and q['ask'] >= self.entryPrice),
            op.do_action(lambda x: print(f'entryTrigger {x}')),
            op.subscribe_on(pool_scheduler)
        )
        self.targetTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.filter(lambda q: self.position > 0 and q['bid'] >= self.targetPrice),
            op.do_action(lambda x: print(f'targetTrigger {x}')),
            op.subscribe_on(pool_scheduler)
        )
        self.stopTrigger = self.market.pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.filter(lambda q: self.position > 0 and q['bid'] <= self.stopPrice),
            op.do_action(lambda x: print(f'stopTrigger {x}')),
            op.subscribe_on(pool_scheduler)
        )
        self.subscriptions = {}


    def setupTrade(self, qty, entry, target, stop):
        self.quantity = qty
        self.entryPrice = entry
        self.targetPrice = target
        self.stopPrice = stop

        self.subscriptions['monitor'] = self.monitor.subscribe(
            lambda x: print(x),
            scheduler=pool_scheduler
        )

        self.subscriptions['entryTrigger'] = self.entryTrigger.subscribe(
            lambda x: self.openPosition(),
            scheduler=pool_scheduler
        )

        self.subscriptions['targetTrigger'] = self.targetTrigger.subscribe(
            lambda x: self.closePosition(),
            scheduler=pool_scheduler
        )

        self.subscriptions['stopTrigger'] = self.stopTrigger.subscribe(
            lambda x: self.closePosition(),
            scheduler=pool_scheduler
        )


    def openPosition(self):
        print(f'bought {self.quantity} {self.ticker}')
        self.position = self.quantity

    def closePosition(self):
        print(f'sold {self.quantity} {self.ticker}')
        self.position = 0


    def dispose(self):
        print('dispose')
        if 'entryTrigger' in self.subscriptions and self.position > 0:
            self.subscriptions['entryTrigger'].dispose()
            del self.subscriptions['entryTrigger']
        if 'targetTrigger' in self.subscriptions and self.position == 0:
            self.subscriptions['targetTrigger'].dispose()
            del self.subscriptions['targetTrigger']
        if 'stopTrigger' in self.subscriptions and self.position == 0:
            self.subscriptions['stopTrigger'].dispose()
            del self.subscriptions['stopTrigger']
        if 'monitor' in self.subscriptions:
            self.subscriptions['monitor'].dispose()
            del self.subscriptions['monitor']
