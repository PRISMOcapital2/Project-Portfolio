import pandas as pd
import time
import pickle
import os
import numpy as np
from numpy import *
from getdata import GetData
from time import gmtime, strftime
from strategy import Strategy
import sys

class Live(object):

    def __init__(self, exchange, currenceyAr, period, directory, name, evec, lookback, liveSimulation = False):
        self.orderBookColumns = ['ORDER_TYPE','DATE', 'PRICE', 'CURRENCEY','ASSET', 'QUANTITY', 'ORDER_ID']
        self.directory = directory
        self.startTime = time.time()
        self.startTimeStr =  strftime("__%Y_%m_%d__%H_%M_%S__",gmtime())
        self.name = name            #for naming the orderbook based on cointegrated assets
        self.eigenvector = evec
        self.lookback = lookback
        self.period = period
        self.liveSimulation = liveSimulation
        self.currenceyAr = currenceyAr
        self.count = 0
        
        if liveSimulation==True:
            self.data = fetch_data(currenceyAr, exchange, directory, period)
        self.priceHistory = None 
        self.localPriceHistoryLength = 100
        self.portfolio = None

        self.trade = Strategy(evec, lookback,self.orderBookColumns, self.currenceyAr) #initialise the strategy object here so we're not repeating ourselves over and over
        self.previous_MV = None
        self.pnl = []

    def tick(self, priceList=False, count = False,date=False): #false if this is a simulated live setting
        #check status of current order book. If the order book doesnt exist (delete if you want to re-start) then it creates a blank one.

        #order book - all open, closed trades
        if not os.path.isfile(self.directory+'orderbooks/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'orderBook.csv'):
            df = pd.DataFrame([[float(0)]*len(self.orderBookColumns)],columns = self.orderBookColumns)
            df.to_csv(self.directory+'orderbooks/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'orderBook.csv',encoding='utf-8',index=False)

        #open order book - only the open orders
        if not os.path.isfile(self.directory+'current_data/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'openOrderBook.csv'):
            df = pd.DataFrame([[float(0)]*len(self.orderBookColumns)],columns = self.orderBookColumns)
            df.to_csv(self.directory+'current_data/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'openOrderBook.csv',encoding='utf-8',index=False)

        #portfolio of currently owned assets
        if not os.path.isfile(self.directory+'portfolio.csv'):
            self.portfolio = pd.DataFrame([[float(0)]*len(self.currenceyAr)]*2,columns = self.currenceyAr, index=['dollarValue','quantity'])
            self.portfolio = self.portfolio.reindex(['dollarValue','quantity'])
            self.portfolio.to_csv(self.directory+self.name+'portfolio.csv',encoding='utf-8')
            
        #orderID and priceHistory
        if not os.path.isfile(self.directory+'current_data/'+self.name+'_'+self.period+'_'+'orderID.pickle'):
            pickler(self.directory+'current_data/'+self.name+'_'+self.period+'_'+'orderID.pickle',1)
        if not os.path.isfile(self.directory+'Raw_data/live_data_storage/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'priceHistory.csv'):
            df = pd.DataFrame(priceList)
            df.to_csv(self.directory+'Raw_data/live_data_storage/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'priceHistory.csv',encoding='utf-8')
            
        #if all the above exist, then get going
        if os.path.isfile(self.directory+'current_data/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'openOrderBook.csv') and os.path.isfile(self.directory+'current_data/'+self.name+'_'+self.period+'_'+'orderID.pickle') and os.path.isfile(self.directory+self.name+'portfolio.csv'):
            openOrderBook = pd.read_csv(self.directory+'current_data/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'openOrderBook.csv')
            orderBook = pd.read_csv(self.directory+'orderbooks/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'orderBook.csv')
            self.portfolio = pd.read_csv(self.directory+self.name+'portfolio.csv',index_col=0)
            orderID = dePickler(self.directory+'current_data/'+self.name+'_'+self.period+'_'+'orderID.pickle')
        else:
            print('A file is missing. It\'s either: the orderBook, orderID or portfolio')
            sys.exit(2)
            

        
        #get data. This will vary based on a simulated live setting, or a true live setting. The latter is easier, so I'll do that first. The prior
        #requires connecting to TWS which will be done later. cos it nastay.
        '''simulated live'''
        if self.liveSimulation==True:
            #saving the price list to the data
            df = pd.DataFrame([priceList])
            df.to_csv(self.directory+'Raw_data/live_data_storage/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'priceHistory.csv', mode='a', header=False,index=False)

            #saving the data to a local dataframe so we don't have to load the entire price history every iteration
            if not isinstance(self.priceHistory, pd.DataFrame):
                self.priceHistory = pd.DataFrame([priceList], columns = self.currenceyAr)
            elif len(self.priceHistory)<self.localPriceHistoryLength:
                self.priceHistory = self.priceHistory.append(pd.DataFrame([priceList], columns=self.currenceyAr),ignore_index=True)
            else:
                self.priceHistory = self.priceHistory.drop(self.priceHistory.index[0])
                self.priceHistory = self.priceHistory.append(pd.DataFrame([priceList], columns=self.currenceyAr),ignore_index=True)

                
        '''live'''
        if self.liveSimulation==True:
            #priceList = None #This is what we're trynna get from TWS
            #save price list
            #load important information into a dataframe
            pass



        #given the price list, MAKE TRADING DECISION, return updates orderBook (ilc. closed orders), and openOrderBook
        openOrderBook, orderBook, self.portfolio, orderID = self.trade.movingAverageLinear([priceList], self.priceHistory, orderBook, openOrderBook, self.portfolio, orderID, self.count)
        

        #store in order book
        self.count +=1
        orderID+=1
        self.pnl.append(self.trade.profit)
        if isinstance(openOrderBook, pd.DataFrame):
            print('PORTFOLIO:\n',self.portfolio,'\n\nOpen Orders:\n',openOrderBook,'\n\n\n')
            #save the orderbooks for the next tick
            pickler(self.directory+'current_data/'+self.name+'_'+self.period+'_'+'orderID.pickle',orderID)
            openOrderBook.to_csv(self.directory+'current_data/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'openOrderBook.csv', encoding='utf-8',index=False)
            orderBook.to_csv(self.directory+'orderbooks/'+self.name+'_'+self.period+'_'+self.startTimeStr+'_'+'orderBook.csv', encoding='utf-8',index=False)
            self.portfolio.to_csv(self.directory+self.name+'portfolio.csv', encoding='utf-8')
            

                         
def fetch_data(currenceyAr, exchange, directory, period):
    if currenceyAr[0] in 'ewcewaige':
        EWCEWAIGE = pd.read_csv('EWCEWAIGE.csv').set_index('date')
    else:
        dataObj = GetData(exchange, directory)
    currenceyPairs = []
    currenceyTsLengths = []
    for currencey in currenceyAr:
        if currencey == 'ewc' or currencey == 'ewa' or currencey == 'ige':
            currenceyPairs.append(EWCEWAIGE[currencey].values)
            currenceyTsLengths.append(len(EWCEWAIGE[currencey].values))
        else:
            ts = dataObj.fetch(currencey)
            ts = dataObj.periodFormatter(currencey, period)
            ts.index = pd.to_datetime(ts.index).dropna()
            currenceyTsLengths.append(len(ts.Close.values))
            currenceyPairs.append(ts.Close.values)          
    maxLen = 20000
    for count, curr in enumerate(currenceyPairs):
        if min(currenceyTsLengths)<maxLen:
            currenceyPairs[count]=curr[-min(currenceyTsLengths):]
        else:
            currenceyPairs[count]=curr[-maxLen:]
    A = []
    for curr in currenceyPairs:
        A.append(curr)
    A = np.transpose(np.array(A))
    return A

def pickler(directory, data):
    pickle_out = open(directory,'wb')
    pickle.dump(data,pickle_out)
    pickle_out.close()
    
def dePickler(directory):
    pickle_in = open(directory,'rb')
    return pickle.load(pickle_in)
