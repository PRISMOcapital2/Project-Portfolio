
class Indicators(object):

    def __init__(self, data_in=None):
        self.prices = []
        self.percentChangelist = []
        self.SMAlist = []
        self.previousEMAslow = None
        self.previousEMAfast = None
        self.previousMACD = None
        self.previousMACDema = None
        self.EMAslow = []
        self.EMAfast = []
        self.MACD = []
        self.signal = []  #9 day EMA of the MACD
        self.smaDiff = []

    def tick(self, price, SMAlength = 25, slow = 26, fast = 12, signal = 9):
        self.prices.append(price)
        #basics
        self.percentchange()
        self.SMAlist.append(self.SMA(self.prices, SMAlength))
        if self.SMAlist[-1] != None:
            self.smaDiff.append(round(float(((price-self.SMAlist[-1])/self.SMAlist[-1])),4))
        else:
            self.smaDiff.append(float(0))

        #EMA and MACD
        self.previousEMAslow = self.EMA(self.prices, slow, self.previousEMAslow)
        self.previousEMAfast = self.EMA(self.prices, fast, self.previousEMAfast)
        self.EMAfast.append(self.previousEMAfast)
        self.EMAslow.append(self.previousEMAslow)

        if len(self.prices)>slow:
            self.MACD.append(self.EMAfast[-1]-self.EMAslow[-1])
            self.previousMACDema = self.EMA(self.MACD, signal, self.previousMACDema)
            self.signal.append(self.previousMACDema)
        else:
            self.MACD.append(None)
            self.signal.append(None)
##        print(self.EMAfast,self.EMAslow)
        
    def percentchange(self):
        if len(self.prices)>1:
            self.percentChangelist.append(float(self.prices[-1]-self.prices[-2])/self.prices[-1])
        else:
            self.percentChangelist.append(None)

    def SMA(self, data, length):
        if len(data)>=length:
            return sum(data[-length:])/length
        else:
            return (None)
       

    def EMA(self, price_data, length, previousEMA = None):        
        if len(price_data)<length:
            return (None)
        else:
            c = 2/float(length+1)
            if previousEMA==None:
                return (self.EMA(price_data, length, self.SMA(self.prices, length)))
            else:
                return (c*price_data[-1]+(1-c)*previousEMA)
