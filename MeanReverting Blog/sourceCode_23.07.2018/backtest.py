from getdata import GetData
from statsmodels.tsa.stattools import adfuller, acf, pacf,arma_order_select_ic
import numpy as np
from numpy import *
import pandas as pd
import pickle
import statsmodels.formula.api as smf
import statsmodels.tsa.api as smt
import statsmodels.api as sm
import scipy.stats as scs
from arch import arch_model
import time
import matplotlib.pyplot as plt
import math
from math import pi, exp
from numpy import cumsum, log, polyfit, sqrt, std, subtract, square, var, log10
from johansen import coint_johansen
from numpy.matlib import repmat
import os
from time import gmtime, strftime

class Backtest(object):
    
    def __init__(self, exchange, currenceyAr, period, directory, livePreScreen=False):

        #set object parameters 
        self.exchange=exchange
        self.period = period
        self.directory = directory
        self.currenceyAr = currenceyAr

        #This is the data set from ernie chan's book ( -x ernie )
        self.EWCEWAIGE = pd.read_csv('EWCEWAIGE.csv').set_index('date')

        #This creates a data object that can be used to fetch data for individually
        #selected exchanged and currencies
        dataObj = GetData(self.exchange, self.directory)


        #Initialising Arrays
        self.currenceyTs = []           #List of vectors containing each time series
        self.currenceyTsLengths = []    #Length of each time series  (used so we can match the lengths of time series (how far back in time they go)
        

        #Iterate through all of the currencies inserted in the command. if "-m ewc, ewa, ige" are insterted as currencies for "-x ernie", it uses the data from the spreadsheets. If not, it uses the GetData module to pull data using ccxt.
        for currencey in currenceyAr:
            if currencey == 'ewc' or currencey == 'ewa' or currencey == 'ige':
                self.currenceyTs.append(self.EWCEWAIGE[currencey].values)
                self.currenceyTsLengths.append(len(self.EWCEWAIGE[currencey].values))
            else:
                ts = dataObj.fetch(currencey)
                ts = dataObj.periodFormatter(currencey, period)
                ts.index = pd.to_datetime(ts.index).dropna()
                self.currenceyTsLengths.append(len(ts.Close.values))
                self.currenceyTs.append(ts.Close.values)


        #This matches the length of the time series. If the length is < 50000, we set the length to the minimum length in our currency.
        for count, currenceyTs_temp in enumerate(self.currenceyTs):
            if min(self.currenceyTsLengths)<50000:
                self.currenceyTs[count]=currenceyTs_temp[-min(self.currenceyTsLengths):]
            else:
                self.currenceyTs[count]=currenceyTs_temp[-50000:]


    #Test for stationarity, recieve p values and lookback time.
    def test_stationarity(self):
        
        #Slap that shit into a matrix. Rows are each time series, columns each time step.
        A = np.transpose(np.matrix(self.currenceyTs))

        #Test for a cointegrated series (do they change in the same direction)
        lookback, evec = cointegrated_series(A, self.period, statTest=True)

        #save the [eigenvector, lookback, date] - so we can use when going live
        name = ''
        for curr in self.currenceyAr:
            name = name + curr
        name = name + '_simple_linear_strategy.pickle'

        save_dir = self.directory+'backtestedParameters/'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_dir = save_dir+name

        pickler(save_dir,[evec, lookback, strftime("%Y-%m-%d %H:%M:%S",gmtime())])

def cointegrated_series(Ar, period, statTest = True):
    
    #Johansen test is a statistical test, testing the hypothesis that r=0, r=1 etc... Where r is the number of cointegrated time series.  This function returns the eigenvector with the largest eigenvector (most profit)
    johansenTest = coint_johansen(Ar,0,2)

    #halfLife_coint returns the lookback time for the cointegrated portfolio under the eigenvector found above. It also returns the marketvalue array and the eigenvector found above.
    lookback, marketVal, evec = halfLife_coint(Ar, johansenTest.evec[:,0])
    lookback = int(lookback)
    print(lookback)
    marketVal = pd.DataFrame(marketVal)

    #simple linear trading strategy: seek to own a number of units equal to the difference of the market value from the marketVal moving average divided by the moving marketVal standard deviation. (i.e. z-score from the MA)
##    MA = pd.DataFrame(np.transpose(movingAve(marketVal.values, lookback)))
##    SD = pd.DataFrame(np.transpose(movingStd(marketVal.values, lookback)))
    MA = pd.rolling_mean(marketVal,lookback)
    SD = pd.rolling_std(marketVal, lookback)
    numUnits = -(marketVal-MA)/SD

    #we want to create a positions matrix, corresponding to the proportionality given by the eigenvector multiplied by the price of the stock, multiplied by the number of units given above.
    LHS = repmat(numUnits,1,len(np.transpose(Ar)))
    RHS = np.multiply(repmat(evec,len(Ar),1),Ar)
    positions = np.multiply(LHS,RHS)
    
    
    #we can gain a rudimentary indication of profit potential by buying and selling stocks every at every ticker. We buy the (numUnits)*(proportionality constant given by eigenvector) at the current price. positions hence corresponds to
    #the value of our portfolio at the current price. pnl = (portfolio market value at previous timesetp) * (ratio of change in price) = positions[-
    pnl = np.sum(divide(multiply(np.roll(positions[:-1],-1),diff(Ar,axis = 0)), np.roll(Ar[:-1],-1)),1)
    pnlCumSum = [0]*len(pnl)
    for count, pnlsum in enumerate(pnl):
        if count>=int(lookback):
            pnlCumSum[count]+=pnlCumSum[count-1]+pnlsum
        else:
            pnlCumSum[count]=0

    if statTest==True:
        print('Lookback:\t',lookback)

    returnsCumSum = [0]*len(pnl)
    for count, pnlsum in enumerate(pnl):
        if count>=int(lookback):
            returnsCumSum[count]+=returnsCumSum[count-1]+pnlsum/np.sum(np.abs(positions[count]))
        else:
            returnsCumSum[count]=0

    
    plt.plot(returnsCumSum)
    plt.xlabel('ticks: '+period)
    plt.ylabel('cumulative returns')
    plt.show()
    
    return lookback, evec
    
def halfLife_coint(A, evec):
    #marketVal is the sum of the value of a portfolio where we own an amount of units of each stock proportional to the value given in the eigenvector at each timeframe.
    #We obtain this by finding the dot product of the array inputted and the eigenvector. For some reason it optputs a row vector, so we transpose it too.
    marketVal = np.transpose(dot(A,evec))

    #marketValChange is the difference in the market value at each time step
    marketValChange = np.diff(marketVal,axis=0)

    #Add a list of 1's so we have an intercept
    marketVal_withOnes = np.hstack([marketVal[1:],np.ones((len(marketVal[1:]),1))])

    #regress these bad boys
    beta = np.linalg.lstsq(marketVal_withOnes, marketValChange, rcond=1)
    half_life = log(2) / beta[0]
    return half_life[0], marketVal, evec

def movingAve(y, length):
        ma = [0]*len(y)
        for count, price in enumerate(y):
            if count>length:
                ma[count]=float((sum(y[count+1-int(length):count+1])/int(length+1)))
        return np.transpose(pd.rolling_mean(y,length))
    
def movingStd(y, length):
    std = [0]*len(y)
    for count, price in enumerate(y):
        if count>length:
            std[count]=np.std(y[count-int(length):count])
        else:
            std[count]=1
    return np.transpose(np.matrix(pd.rolling_std(y,length)))

        #idk how this works lol
def half_life(y):
    lag = y.shift(1)
    lag[0]=0
    deltaY = y-lag
    deltaY[0]=0
    lagConst = sm.add_constant(lag) # adds a intercept value to the x variable
    model = sm.OLS(list(deltaY), lagConst)
    res = model.fit()
    halfLife = -math.log(2)/res.params[1]
    return halfLife

def hurst_ernie_chan(p):
    lags = range(2,20)
    variancetau = []; tau = []
    for lag in lags: 
        tau.append(lag)
        pp = subtract(p[lag:], p[:-lag])
        variancetau.append(np.var(pp))
    m = polyfit(np.log10(tau),np.log10(variancetau),1)
    hurst = m[0] / 2
    return hurst

def adf(ts):
    adf = adfuller(ts, autolag='AIC')
    dfoutput = pd.Series(adf[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in adf[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)
    
def normcdf(X):
    (a1,a2,a3,a4,a5) = (0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429)
    L = abs(X)
    K = 1.0 / (1.0 + 0.2316419 * L)
    w = 1.0 - 1.0 / sqrt(2*pi)*exp(-L*L/2.) * (a1*K + a2*K*K + a3*pow(K,3) + a4*pow(K,4) + a5*pow(K,5))
    if X<0:
        w = 1.0-w
    return w

def vratio(a, lag = 2, cor = 'hom'): #takes a dataframe as entry
    t = (std((a[lag:]) - (a[1:-lag+1])))**2;
    b = (std((a[2:]) - (a[1:-1]) ))**2;
    n = int(len(a))
    mu  = sum(a[1:n]-a[:-1])/n;
    m=(n-lag+1)*(1-lag/n);
#   print mu, m, lag
    b=sum(square(a[1:n]-a[:n-1]-mu))/(n-1)
    t=sum(square(a[lag:n]-a[:n-lag]-lag*mu))/m
    vratio = t/(lag*b);
    la = float(lag)
 
    if cor == 'hom':
        varvrt=2*(2*la-1)*(la-1)/(3*la*n)
 
    elif cor == 'het':
          varvrt=0;
          sum2=sum(square(a[1:n]-a[:n-1]-mu)); 
          for j in range(lag-1):
             sum1a=square(a[j+1:n]-a[j:n-1]-mu); 
             sum1b=square(a[1:n-j]-a[0:n-j-1]-mu)
             sum1=dot(sum1a,sum1b); 
             delta=sum1/(sum2**2);
             varvrt=varvrt+((2*(la-j)/la)**2)*delta
 
    zscore = (vratio - 1) / math.sqrt(float(varvrt))
    pval = normcdf(zscore);
 
    return  vratio, zscore, pval

def pickler(directory, data):
    pickle_out = open(directory,'wb')
    pickle.dump(data,pickle_out)
    pickle_out.close()
    
def dePickler(directory):
    pickle_in = open(directory,'rb')
    return pickle.load(pickle_in)

def tsplot(y, lags=None, figsize=(10,8), style='bmh'):
    if not isinstance(y, pd.Series):
        y = pd.Series(y)
    with plt.style.context(style):
        fig = plt.figure(figsize=figsize)
        layout = (3,2)
        timeseries_ax = plt.subplot2grid( layout, (0,0), colspan = 2)
        autocorrelation_ax = plt.subplot2grid( layout, (1,0), colspan = 1)
        partial_autocorrelation_ax = plt.subplot2grid( layout, (1,1), colspan = 1)
        quantile_ax = plt.subplot2grid( layout, (2,0), colspan = 1)
        probability_ax = plt.subplot2grid( layout, (2,1), colspan = 1)

        y.plot(ax = timeseries_ax)
        timeseries_ax.set_title('Time Series Analysis Plots')
        smt.graphics.plot_acf(y, lags=lags, ax=autocorrelation_ax, alpha=0.5)
        smt.graphics.plot_pacf(y, lags=lags, ax=partial_autocorrelation_ax, alpha=0.5)
        sm.qqplot(y, line='s', ax=quantile_ax)
        scs.probplot(y, sparams=(y.mean(), y.std()), plot = probability_ax)

        plt.tight_layout()
        plt.show()
    return
##    def test_stationarity(self):
##        #Divide data into smaller data sets for quicker tests
##        length = len(self.ts)
##        start = int(length/5)
##        endTest = int(start/2)
##        close = self.ts.Close[-start:-endTest]
##
##        #Find the hurst exponent & test with var-ratio,
##        #compute and ADF test stat then find half life of mean reversion
##        print('\n\nHurst\t',hurst_ernie_chan(close))
##        print('\n\nADF test:\n')
##        adf(close)
##        print('\n\nVariance Ratio Test:\n',vratio(log(close).values))
##        lookback = half_life(pd.Series(close))
##        print('\n\nLookback:\n',lookback)
##
##        #calculate the moving average and moving standard deviation with lookback equal to the half life
##        MA = movingAve(close[-endTest:], lookback)
##        SD = movingStd(close[-endTest:], lookback)
##
##        #the market value is equal to the negative normalised deviation from its moving average
##        mktVal = []
##        for count, price in enumerate(close[-endTest:]):
##            if SD[count]==0:
##                mktVal.append(0)
##            else:
##                mktVal.append(-(price-MA[count])/SD[count])
##        pnl = [0]*endTest
##        for count, p in enumerate(mktVal):
##            if SD[count]==0:
##                pnl[count]=0
##            else:
##                pnl[count]=pnl[count-1]+mktVal[count-1]*(close[-endTest:][count]-close[-endTest:][count-1])/close[-endTest:][count-1]
##        plt.plot(pnl)
##        plt.show()
                
##    def test_stationarity(self): #test on CADUSD
##        close = self.USDCAD.iloc[:,0].dropna().values
##        print('\n\nHurst\t',hurst_ernie_chan(close))
##        print('\n\nADF test:\n')
##        adf(close)
##        print('\n\nVariance Ratio Test:\n',vratio(log(close)))
##        lookback = half_life(pd.Series(close))
##        print('\n\nLookback:\n',lookback)
##        MA = movingAve(close, lookback)
##        SD = movingStd(close, lookback)
##        mktVal = []
##        for count, price in enumerate(close):
##            if SD[count]==0:
##                mktVal.append(0)
##            else:
##                mktVal.append(-(price-MA[count])/SD[count])
##
##        pnl = [0]*len(close)
##        for count, p in enumerate(mktVal):
##            if count==0:
##                pnl[count]=0
##            else: 
##                pnl[count]=pnl[count-1]+mktVal[count-1]*(close[count]-close[count-1])/close[count-1]
##        plt.plot(pnl)
##        plt.xlabel('time')
##        plt.ylabel('cumulative P&L')
##        plt.show()
