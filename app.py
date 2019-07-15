from rx import of, create, operators as op

from quotesource import market
from trade import Trade

def main():
    nflx = Trade('NFLX', market)
    aapl = Trade('AAPL', market)
    amzn = Trade('AMZN', market)
    fb = Trade('FB', market)
    googl = Trade('GOOGL', market)

if __name__ == '__main__':
    main()
