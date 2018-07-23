from indicators import Indicators
import pandas as pd
import numpy as np
from numpy import *
import time
from numpy.matlib import repmat


class Live(object):
    def __init__(self, lookback, eigenvector, pseudoLive=True):
        #pseudoLive is where I run the 'live' algorithm on historical data
        self.lookback=lookback
        self.eigenvector = eigenvector
        self.priceAr = []
        
        self.pnl = 0
        self.pnlCumSum = []
        self.returnsCumSum = []
        self.returns = 0

        self.marketValue = []
        self.positions = []

        #self.indicators.priceAr =  [[ts1, ts2, ... ], [ts1, ts2, ...] ... ]
        self.indicators = Indicators(lookback)

        
        self.openTradesAr = []
        self.balance = 0



        
    def tick(self, priceList, count):
        print(self.portfolio)
        self.priceAr.append(priceList)
        if count > self.lookback:
            #calculate pnl from previous trade
            pnl = np.sum(multiply(self.positions[-1],divide(subtract(self.priceAr[-1],self.priceAr[-2]),self.priceAr[-2])))
            self.pnlCumSum.append(self.pnlCumSum[-1]+pnl)
            if np.sum(np.abs(self.positions[-1])) == 0:
                value = 1
            else:
                value = np.sum(np.abs(np.array(self.positions[-1])))
            self.returnsCumSum.append(divide(float(pnl),value))

            for i, trade in enumerate(self.openTradesAr):
                if trade[0]=='BUY':
                    self.balance+=-priceList[0,i]*trade[2]*trade[3]
                elif trade[0]=='SELL':
                    self.balance+=-priceList[0,i]*trade[2]*trade[3]
            self.openTrades = []
            
            #find new parameters
            marketValue = self.eigenvector*transpose(priceList)
            self.marketValue.append(marketValue)
            self.indicators.tick(self.marketValue, count)
            numUnits = -(marketValue-self.indicators.movingAverage[-1])/self.indicators.movingStd[-1]
            positions = multiply(multiply(self.eigenvector,priceList),repmat(numUnits,1,priceList.size))

            openTrades = []
            for i in range(size(positions)):
                if positions[0,i]>0:
                    openTrades.append(['BUY',priceList[0,i],self.eigenvector[i],numUnits[0,0],positions[0,i]])
                else:
                    openTrades.append(['SELL',priceList[0,i],self.eigenvector[i],numUnits[0,0],positions[0,i]])
                self.balance += priceList[0,i]*self.eigenvector[i]*numUnits[0,0]

            print(self.balance)
            
            self.openTradesAr.append(openTrades)
            
            self.positions.append(positions)

            
        else:
            marketValue = self.eigenvector*transpose(priceList)
            self.marketValue.append(marketValue)
            
            self.indicators.tick(self.marketValue, count)

            self.positions.append([0]*len(priceList))
            
            self.pnlCumSum.append(0)
            self.returnsCumSum.append(float(0))
