from numpy import *
import pandas as pd
import time

class Indicators(object):

    def __init__(self, lookback):
        self.lookback = lookback

        self.movingAverage = []
        self.movingStd = []
        
    def tick(self, priceList, count):   
        movingA = movingAve(priceList,self.lookback, count)
        movingS = movingStd(priceList,self.lookback, count)
        self.movingAverage.append(movingA)
        self.movingStd.append(movingS)
        
        
def movingStd(y, lookback, count):
    if count>= lookback:
        return std(y[-lookback:])
    else:
        return 1

def movingAve(y, lookback, count):
    if count>= lookback:
        return sum(y[-lookback+1:])/lookback
    else:
        return 0  
