from rx import of, create, operators as op

import config
from stock import Stock

def main():
    config.quoteObserver.requestQuotes('AAPL,AMZN,GOOGL,FB,NFLX')
    config.stocks['AAPL'] = Stock(config.quoteObserver, 'AAPL')
    config.stocks['AMZN'] = Stock(config.quoteObserver, 'AMZN')
    config.stocks['GOOGL'] = Stock(config.quoteObserver, 'GOOGL')
    config.stocks['FB'] = Stock(config.quoteObserver, 'FB')
    config.stocks['NFLX'] = Stock(config.quoteObserver, 'NFLX')

if __name__ == '__main__':
    main()
    input('Press <enter> to quit')
