class Indicators(object):

    def __init__(self):
        pass

    def SMA(self, prices, length):
        if prices:
            return sum(prices[-length:])/length
        else:
            return None

    def EMA(self, price_data, length, previousEMA = False):
        if len(price_data)<length:
            return None
        c = 2/float(length+1)
        if not previousEMA:
            return self.EMA(price_data,length,self.SMA(price_data,length))
        else:
            return c*price[-1]+(1-c)*previousEMA
        
