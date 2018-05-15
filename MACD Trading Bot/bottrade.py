class BotTrade(object):

    def __init__(self, price, vol, print_val = True):
        self.status = 'OPEN'
        self.volume = vol
        self.entryPrice = price
        self.exitPrice = 0
        self.print = print_val
        if self.print:
            print(self.entryPrice, self.volume)
            print('Trade Opened')

    def close(self, price):
        self.status = 'CLOSED'
        self.exitPrice = price
        if self.print:
            print('TradeClosed')

    

    def profit(self):
        return float(self.exitPrice-self.entryPrice)
        
