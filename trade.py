import rx
from rx import of, from_, create, operators as op
from rx.concurrency import ThreadPoolScheduler
import multiprocessing
import logging

thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(thread_count)

logging.basicConfig(level=logging.INFO, format="[%(threadName)-23s] %(asctime)-15s %(message)s ")

class Trade:
    def __init__(self, ticker, market):
        self.ticker = ticker
        self.position = 0
        self.quantity = -1
        self.entryPrice = -1
        self.targetPrice = -1
        self.stopPrice = -1
        self.market = create(lambda o,s: market(o,s)).pipe(
            op.filter(lambda v: v['symbol'] == self.ticker),
            op.subscribe_on(pool_scheduler),
            op.observe_on(pool_scheduler),
            op.publish()
        )
        self.monitor = self.market.pipe(
            #op.do_action(print),
            op.subscribe_on(pool_scheduler),
            op.observe_on(pool_scheduler)
        )
        self.entryTrigger = self.market.pipe(
            op.filter(lambda q: self.position == 0 and q['ask'] >= self.entryPrice),
            op.do_action(lambda x: logging.info(f'entryTrigger {x}')),
            op.subscribe_on(pool_scheduler),
            op.observe_on(pool_scheduler)
        )
        self.targetTrigger = self.market.pipe(
            op.filter(lambda q: self.position > 0 and q['bid'] >= self.targetPrice),
            op.do_action(lambda x: logging.info(f'targetTrigger {x}')),
            op.subscribe_on(pool_scheduler),
            op.observe_on(pool_scheduler)
        )
        self.stopTrigger = self.market.pipe(
            op.filter(lambda q: self.position > 0 and q['bid'] <= self.stopPrice),
            op.do_action(lambda x: logging.info(f'stopTrigger {x}')),
            op.subscribe_on(pool_scheduler),
            op.observe_on(pool_scheduler)
        )
        self.subscriptions = {}


    def setupTrade(self, qty, entry, target, stop):
        self.quantity = qty
        self.entryPrice = entry
        self.targetPrice = target
        self.stopPrice = stop

        self.subscriptions['monitor'] = self.monitor.subscribe(
            lambda x: logging.info(x),
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

        self.market.connect()


    def openPosition(self):
        logging.info(f'bought {self.quantity} {self.ticker}')
        self.position = self.quantity
        self.subscriptions['entryTrigger'].dispose()
        del self.subscriptions['entryTrigger']


    def closePosition(self):
        logging.info(f'sold {self.quantity} {self.ticker}')
        self.position = 0


    def dispose(self):
        logging.info('dispose')
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
