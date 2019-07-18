from rx import of, create, operators as op

from quotesource import market
from trade import Trade

def main():
    nflx = Trade('NFLX', market)
    aapl = Trade('AAPL', market)
    amzn = Trade('AMZN', market)
    fb = Trade('FB', market)
    googl = Trade('GOOGL', market)
    nflx.setupTrade(100, 375.25, 376.5, 375)
    aapl.setupTrade(100, 199.25, 199.5, 198.75)
    amzn.setupTrade(100, 1999.25, 2000.5, 1998)

if __name__ == '__main__':
    main()
    input('Press <enter> to quit')
