import pandas as pd
import random
from time import gmtime, strftime
from indicators import Indicators
import numpy as np
import time
class Strategy(object):

    def __init__(self, eigenvector, lookback, columns, currenceyAr):
        self.eigenvector = eigenvector
        self.lookback = lookback
        self.orderBookColumns = columns

        #create an indicator object. Here we store the moving average and std for the market value
        self.indicators = Indicators(self.lookback)
        self.currenceyAr = currenceyAr

        #marketaValueHistory is the last <lookback> values for market value. Trade count is so we don't try to sell anything before we've even made a trade
        self.marketValueHistory = []
        self.tradeCount = 0
        self.profit = 0

        
    def movingAverageLinear(self, currentPrice, priceHistory, orderBook, openOrderBook, portfolio, orderID, tickCount):
        #create a new blank openOrderBook and portfolio, which we'll update whenever a trade is made
        openOrderBook_NEW = None
        portfolio_NEW = portfolio

        #iterate through all open trades from the previous trading session. Sell them all in this strategy.
        if self.tradeCount>=1:
            for index, row in openOrderBook.iterrows():
                
                #put the order into a list, easier to use
                order = [row.ORDER_TYPE,row.DATE,row.PRICE,row.CURRENCEY,row.QUANTITY, row.ASSET, row.ORDER_ID]
                price_opened = row.PRICE
                asset = row.ASSET
                quantity = row.QUANTITY

                #CLOSE - we close all the trades opened in the previous session
                if True:
                    
                    #connect to TWS here
                    
                    currentPriceInt = currentPrice[0][self.currenceyAr.index(asset)]

                    #if we bought on the previous session, we sell back the quantity we bought at the new price
                    if quantity >=0: 
                        order = self.SELL(asset, currentPriceInt, quantity, orderID)
                        orderID+=1
                        self.tradeCount+=1
                        portfolio_NEW.at['dollarValue',asset] = portfolio_NEW.at['dollarValue',asset]+currentPriceInt*abs(quantity)
                        portfolio_NEW.at['quantity',asset] = portfolio_NEW.at['quantity',asset]-abs(quantity)

                        #selling the difference in what we sold the asset at, minus what we sell them for
                        self.profit+=abs(quantity)*(currentPriceInt-price_opened)

                    #sold on previous session, buy back the asset
                    if quantity<0: 
                        order = self.SELL(asset, currentPriceInt, quantity, orderID)
                        orderID+=1
                        self.tradeCount+=1
                        portfolio_NEW.at['dollarValue',asset] = portfolio_NEW.at['dollarValue',asset]-currentPriceInt*abs(quantity)
                        portfolio_NEW.at['quantity',asset] = portfolio_NEW.at['quantity',asset]+abs(quantity)
                        
                        self.profit-=abs(quantity)*(currentPriceInt-price_opened)

                    #we append the order to the general order book if we make one. This order book stores all open and closed Trades
                    orderBook = orderBook.append(pd.DataFrame([order],columns=self.orderBookColumns), ignore_index=True)

                else:
                    
                    #Here we're NOT SELLING.When we're not selling, we keep the open order (i.e. add it to the newOrderBook)
                    #if the new openOrderBook has nothing in it, create it. If it does, append the still open trade.
                    if not isinstance(openOrderBook_NEW, pd.DataFrame): #if not SELL, keep the trade in new orderBook
                        openOrderBook_NEW = pd.DataFrame([order],columns=self.orderBookColumns)
                    else:
                        openOrderBook_NEW=openOrderBook_NEW.append(pd.DataFrame([order],columns=self.orderBookColumns), ignore_index=True)

        positions = np.multiply(self.eigenvector,currentPrice)
        marketValue = np.dot(self.eigenvector,np.transpose(currentPrice))[0]

        #OPEN- we open orders here.
        #this makes it so that the self.markValHist is always of length 25 (or less)
        if len(self.marketValueHistory)<self.lookback:
            self.marketValueHistory.append(marketValue)
        else:
            del self.marketValueHistory[0]
            self.marketValueHistory.append(marketValue)

        #this updates the moving average and std in the indicator object
        self.indicators.tick(self.marketValueHistory, tickCount)

        
        if tickCount >= self.lookback: #so we have accurate moving averages
            numUnits = -(marketValue-self.indicators.movingAverage[-1])/self.indicators.movingStd[-1]
            '''The essence of this strategy'''

            #iterate through all the assets we have cointegrated, and buy a quantity proportional to the corresponding eigenvector value
            for count, asset in enumerate(self.currenceyAr):
                currentPriceInt = currentPrice[0][count]
                quantity = numUnits*self.eigenvector[count]
                if quantity >=0:
                    order = self.BUY(asset, currentPriceInt, quantity, orderID)
                    orderID+=1
                    self.tradeCount+=1

                    #updating the portfolios
                    portfolio_NEW.at['dollarValue',asset] = portfolio_NEW.at['dollarValue',asset]-currentPriceInt*abs(quantity)
                    portfolio_NEW.at['quantity',asset] = portfolio_NEW.at['quantity',asset]+abs(quantity)
                    
                if quantity<0:
                    order = self.SELL(asset, currentPriceInt, quantity, orderID)
                    orderID+=1
                    self.tradeCount+=1

                    portfolio_NEW.at['dollarValue',asset] = portfolio_NEW.at['dollarValue',asset]+currentPriceInt*abs(quantity)
                    portfolio_NEW.at['quantity',asset] = portfolio_NEW.at['quantity',asset]-abs(quantity)

                orderBook = orderBook.append(pd.DataFrame([order],columns=self.orderBookColumns), ignore_index=True)

                #This adds the newly opened orders to the openOrderBook
                if not isinstance(openOrderBook_NEW, pd.DataFrame):
                    openOrderBook_NEW = pd.DataFrame([order],columns=self.orderBookColumns)
                else:
                    openOrderBook_NEW = openOrderBook_NEW.append(pd.DataFrame([order], columns = self.orderBookColumns), ignore_index=True)

        else:
            pass

        #return the new orderBooks
        return openOrderBook_NEW, orderBook, portfolio_NEW, orderID

    
    def BUY(self,asset, price, quantity, orderID):
        orderType = 'BUY'
        #TWS CONNECTION
        return [orderType,strftime("%Y/%m/%d %H:%M:%S",gmtime()),price,'USD',asset, quantity, orderID]

    def SELL(self ,asset, currentPrice, quantity, orderID):
        #TWS CONNECTION
        orderType = 'SELL'
        return [orderType,strftime("%Y/%m/%d %H:%M:%S",gmtime()),currentPrice,'USD',asset, quantity, orderID]
