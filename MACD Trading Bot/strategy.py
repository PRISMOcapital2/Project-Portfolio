from bottrade import BotTrade
from indicators import Indicators
from graphics import Graphics

class Strategy(object):

    def __init__(self, length, numsimul):
        self.prices = []
        self.btcPrices = []
        self.trades = []
        self.indicators = Indicators()
        self.length = length
        self.USDpertrade = 100

        #binary lists for graphing results
        self.buylist = []
        self.selllist = []

        #profit init
        self.coinVolume = 0
        self.print = False
        self.profit = 0
        self.balance = 0
        self.balanceList = []
        self.numSimul = numsimul
        self.maxDiff = 0
        self.numtrades=0
        
        #moving average init
        self.MAlong = []
        self.MAshort = []

        #MACD init
        self.EMAfast = []
        self.EMAslow = []
        self.previousEMAfast = None
        self.currentEMAfast = None
        self.previousEMAslow = None
        self.currentEMAslow = None
        self.previousEMAmacd = None
        self.currentEMAmacd = None
        self.MACD = []
        self.signal = []

    def tick(self, price, btcPrice=None, indicator = None):
        self.currentPrice = price
        self.currentBTC = btcPrice
        self.btcPrices.append(self.currentBTC)
        self.prices.append(self.currentPrice)

    def movingaverage(self, MAlong, MAshort, count):
        if self.currentBTC == None:
            self.coinVolume = 1
        else:
            buy_volume = self.USDpertrade/self.currentBTC
            self.coinVolume = buy_volume/self.currentPrice
            self.coinVolume = 1
        newOpenedTrades = 0
        newClosedTrades = 0
        openTrades = []

        for trade in self.trades:
            if trade.status == 'OPEN':
                openTrades.append(trade)

        self.MAlong.append(self.indicators.SMA(self.prices,MAlong))
        self.MAshort.append(self.indicators.SMA(self.prices,MAshort))
        
        if self.MAlong[-1]==None:
            pass
        else:
            if self.print:
                print('Price:',self.currentPrice,'\tMAlong:',self.MAlong[-1],
                      'MAshort:',self.MAshort[-1])

            if count > MAlong:
                 if ((self.MAshort[-1])>self.MAlong[-1]):
                    if len(openTrades)<self.numSimul:
                        #need to embed the trade volume into the trade object, otherwise we sell more volume than be buy.
                        self.trades.append(BotTrade(self.currentPrice,self.coinVolume, self.print))
                        newOpenedTrades+=1
                        self.balance -= self.coinVolume*self.trades[-1].entryPrice

        for trade in openTrades:
             if self.MAshort[-1]<self.MAlong[-1]:# or (self.data[count]/trade.entryPrice)>1.05 or (self.data[count]/trade.entryPrice)<0.95:
                newClosedTrades+=1
                
                if count == self.length:
                    trade.close(self.currentPrice)
                else:
                    trade.close(self.currentPrice)
                    
                self.profit+=trade.profit()
                self.balance+=trade.volume*trade.exitPrice

        self.balanceList.append(self.balance)

        if newClosedTrades>0:
                self.selllist.append(True)
        else:
            self.selllist.append(False)

        if newOpenedTrades>0:
            self.buylist.append(True)
        else:
            self.buylist.append(False)
      

    def macd(self, slow, fast, signal, count, lengthPrices):
        if self.currentBTC == None:
            self.coinVolume = self.USDpertrade/self.currentPrice
        else:
            buy_volume = self.USDpertrade/self.currentBTC
            self.coinVolume = buy_volume/self.currentPrice
        newOpenedTrades = 0
        newClosedTrades = 0
        openTrades = []

        for trade in self.trades:
            if trade.status == 'OPEN':
                openTrades.append(trade)
        if len(self.prices)>slow:
            self.previousEMAslow = self.indicators.EMA(self.prices, slow, self.previousEMAslow)
            self.previousEMAfast = self.indicators.EMA(self.prices, fast, self.previousEMAfast)
            self.EMAfast.append(self.previousEMAfast)
            self.EMAslow.append(self.previousEMAslow)

            self.MACD.append(self.EMAfast[-1]-self.EMAslow[-1])
            self.previousEMAmacd = self.indicators.EMA(self.MACD, signal, self.previousEMAmacd)
            self.signal.append(self.previousEMAmacd)

            if len(self.prices)>100:
                self.difference(self.signal[-1]-self.MACD[-1])
                if (self.MACD[-1]>(self.signal[-1]+self.maxDiff/4)) and (self.MACD[-2]>self.signal[-2]):
                    if len(openTrades)<self.numSimul:
                        self.trades.append(BotTrade(self.currentPrice,self.coinVolume, self.print))
                        newOpenedTrades+=1
                        self.balance -= self.coinVolume*self.currentPrice
                        self.numtrades+=1
                        
            for trade in openTrades:
                if ((self.MACD[-1]<self.signal[-1]) and (self.MACD[-2]>self.signal[-2])) or count == lengthPrices-1:
                    trade.close(self.currentPrice)
                    self.balance+=trade.volume*self.currentPrice
                    self.profit+=trade.profit()
                    newClosedTrades+=1


            #graphing section
            self.balanceList.append(self.balance)
            if newClosedTrades>0:
                self.selllist.append(True)
            else:
                self.selllist.append(False)

            if newOpenedTrades>0:
                self.buylist.append(True)
            else:
                self.buylist.append(False)
            
    def difference(self, new):
        if self.maxDiff>abs(new):
            pass
        else:
            self.maxDiff = abs(new)
            
    def returnParam(self):
##        return self.profit, self.balance
        return self.profit
    
        

        











                
