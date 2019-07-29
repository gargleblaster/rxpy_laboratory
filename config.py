import rx
from rx import operators as ops
from rx.concurrency import ThreadPoolScheduler
from quoteobserver import QuoteObserver


accessToken = None
quoteObserver = QuoteObserver()
stocks = {}

import multiprocessing

thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(thread_count)
