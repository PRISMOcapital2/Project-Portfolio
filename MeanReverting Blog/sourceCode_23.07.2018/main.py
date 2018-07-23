import sys, getopt
from backtest import Backtest
from live import Live
from getdata import GetData
import time
import pandas as pd
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import pickle

def main(argv):
    #Fetches input arguments from cmd
    #-p <Period>, -x <Exchange>, -s <State> (backtesting, live or lvie simulation)
    #-c <Currency>, -m <multiple currencies> (insert as a list)
    
    try:
        opts, args = getopt.getopt(argv, 'p:x:s:c:m:')                                       #feed in input from cmd
    except:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-p'):
            if arg.lower() in ['5m','15m','30m','1h','1d']:
                period = arg
            else:
                print('invalid period')
                sys.exit(2)
        if opt in ('-x'):
            if arg.lower() in ['poloniex','snp500','ernie']:
                exchange = arg
            else:
                print('invalid exchange')
                sys.exit(2)
        if opt in ('-s'):
            if arg.lower() in ['live','backtest','livesimul']:
                state=arg
            else:   
                print('invalid state')
                sys.exit(2)
        if opt in ('-c'):
            if exchange == 'poloniex' and arg in ['BTC/USDT','OMG/BTC']:
                currencey=arg
            elif exchange == 'snp500' and arg in ['GOOG']:
                currencey = arg
            elif exchange == 'ernie' and arg in ['ewa','ewc','ige']:
                currencey = arg
            else:
                print('invalid currency for this exchange')
                sys.exit(2)
            currencyAr = [currencey]
                
        if opt in ('-m'): #multiple series
            currencies = arg.split(',')
            for currencey in currencies:
                if exchange=='poloniex' and currencey in ['BTC/USDT','OMG/BTC','ETH/USDT','XMR/USDT']:
                    pass
                elif exchange == 'snp500' and currencey in ['GOOG']:
                    pass
                elif exchange == 'ernie' and currencey in ['ewa','ewc','ige']:
                    pass
                else:
                    print('invalid currency for this exchange')
                    sys.exit(2)
                    break
            currenceyAr = currencies
    for count, curr in enumerate(currenceyAr):
        if '/' in curr:
            currenceyAr[count]=curr.replace('/','_')
    #Data Directory:
    directory = 'C:/Users/Billy/Documents/Code/MeanRevertingStrategy/Data/'

    #Backtesting 
    if state.lower()=='backtest':
        test_model = Backtest(exchange, currenceyAr, period, directory)
        test_model.test_stationarity()

    #Live - Simulated
    if state.lower() == 'pseudolive':
        
        #######
        lookback = 26
        eigenVector = [0.76975358, -0.87789041, 0.08870492]
        ######
        
        liveObj = Live(lookback, eigenVector, pseudoLive=True)
        data = fetch_data(currenceyAr, exchange, directory, period)

        for count, priceList in enumerate(data):
            liveObj.tick(priceList, count)
        print(liveObj.balance)
        returns = []
        returns.append(0)
        for x in liveObj.returnsCumSum:
            returns.append(returns[-1]+x)
        plt.plot(returns)
        plt.show()
        
    #Live
    if state.lower() == 'live' or state.lower() == 'livesimul' :
        
        #This will fetch the parametes from a previous backtest, sorry for gross code
        save_dir, name = directory+'backtestedParameters/',''
        for curr in currenceyAr:
            print(name)
            name = name + curr
        [evec, lookback, date] = dePickler(save_dir+name+'_simple_linear_strategy.pickle')
        print('\n\nUse the Eigenvector: ',evec,'\nWith the lookback of: ',lookback,' periods\nBacktested on the date: ',date,' ?? yes <y>, no <n>: ')
        continueVar = input()

        #run the live module if the user confirms so
        if continueVar == 'y':
            print('starting\n\n')
            liveObj = Live(exchange, currenceyAr, period, directory, name, evec, lookback, state.lower() == 'livesimul')
            if state.lower() == 'livesimul':
                for count, priceList in enumerate(liveObj.data[:1440]):
                    print(count)
                    liveObj.tick(priceList, count)
                plt.plot(liveObj.pnl)
                plt.show()

            else:
                while True:
                    liveObj.fetchPrice()
                    liveObj.tick(priceList)
                    if period == '5m':
                        time.sleep(300)
                    elif period =='10m':
                        time.sleep(600)
                    elif period == '15m':
                        time.sleep(900)
                    elif period == '1h':
                        time.sleep(3600)
                    elif period == '1d':
                        time.sleep(86400)
                    
            
        else:
            sys.exit(2)

        
        


def fetch_data(currenceyAr, exchange, directory, period):
    dataObj = GetData(exchange, directory)
    EWCEWAIGE = pd.read_csv('EWCEWAIGE.csv').set_index('date')
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
        if min(currenceyTsLengths)<10000:
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

if __name__=='__main__':
    print(' -p <period:\t\t 5m, 15m, 30m, 1h, 1d>\n',
          '-x <exchange:\t\t ernie, poloniex, snp500 (broke)\n',
          '-s <algo state:\t backtest, live, pseudolive\n',
          '-c <currency(single):\n',
          '-m <currency(multiple): <comma seperated>')
    main(sys.argv[1:])
