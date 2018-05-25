from getdata import GetData
from statsmodels.tsa.stattools import adfuller, acf, pacf,arma_order_select_ic
import numpy as np
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

class Backtest(object):
    
    def __init__(self, exchange, currencey, period, directory, livePreScreen=False):
        self.exchange=exchange
        self.currencey = currencey
        self.period = period
        self.directory = directory
        
        dataObj = GetData(self.exchange, self.directory)
        self.ts = dataObj.fetch(self.currencey)
        self.ts = dataObj.periodFormatter(self.currencey, period)
        self.ts.index = pd.to_datetime(self.ts.index).dropna()
        
        dataObj = GetData(self.exchange, self.directory)
        self.tsA = dataObj.fetch('XMR/USDT')
        self.tsA = dataObj.periodFormatter('XMR/USDT', period)
        self.tsA.index = pd.to_datetime(self.tsA.index).dropna()
        self.tsB = dataObj.fetch('ETH/USDT')
        self.tsB = dataObj.periodFormatter('ETH/USDT', period)
        self.tsB.index = pd.to_datetime(self.tsB.index).dropna()

        self.USDCAD = pd.read_csv('CADUSD.csv').astype(float).dropna()
        self.EWCEWAIGE = pd.read_csv('EWCEWAIGE.csv').set_index('date')
        
    def test_stationarity(self):
        ewc = self.EWCEWAIGE['ewc'].values
        ewa = self.EWCEWAIGE['ewa'].values
        ige = self.EWCEWAIGE['ige'].values
        
        btc = self.ts.Close[-5000:]
        eth = self.tsA.Close[-5000:]
        xmr = self.tsB.Close[-5000:]
        
        A = []
        A.append(btc)
        A.append(eth)
        A.append(xmr)
        A = np.transpose(np.matrix(A))
        cointegrated_series(A,statTest=True)



def cointegrated_series(Ar, statTest = True):   #Ar =  [[TS(1)E(1), TS(2)E(1), ...TS(n)E(1)]
                                                #       [TS(1)E(2), TS(2)E(2), ...TS(n)E(2)]
                                                #       ...
                                                #       [TS(1)E(n), TS(2)E(n), ...TS(n)E(n)]]
    johansenTest = coint_johansen(Ar,0,2)
    lookback, marketVal, evec = halfLife_coint(Ar, johansenTest.evec[:,0])

    marketVal = pd.DataFrame(marketVal)
    MA = pd.DataFrame(np.transpose(movingAve(marketVal.values, lookback)))
    SD = pd.DataFrame(np.transpose(movingStd(marketVal.values, lookback)))
    numUnits = -(marketVal-MA)/SD
    AA = repmat(numUnits,1,len(np.transpose(Ar)))
    BB = np.multiply(repmat(evec,len(Ar),1),Ar)
    positions = np.multiply(AA,BB)
    pnl = np.sum(np.divide(np.multiply(positions[:-1],np.diff(Ar,axis = 0)), Ar[:-1]),1)
    returns = np.divide(pnl,np.roll(np.sum(abs(positions[:-1]),1),-1))
    
    pnlCumSum = [0]*len(pnl)
    for count, pnlsum in enumerate(returns):
        if count>=int(lookback):
            pnlCumSum[count]+=pnlCumSum[count-1]+pnlsum
        else:
            pnlCumSum[count]=0

    if statTest==True:
        print('Lookback:\t',lookback)
        
    plt.plot(pnlCumSum)
    plt.show()
    
def movingAve(y, length):
        ma = [0]*len(y)
        for count, price in enumerate(y):
            if count>length:
                ma[count]=float((sum(y[count-int(length):count])/int(length)))
        return np.matrix(ma)
    
def halfLife_coint(y, evec):
    marketVal = np.sum(np.multiply(repmat(evec,len(y[1]),1),y),1)
    deltaY = np.diff(marketVal,axis=0)
    yy = np.hstack([marketVal[1:],np.ones((len(marketVal[1:]),1))])
    beta = np.linalg.lstsq(yy, deltaY)
    half_life = log(2) / beta[0]
    return half_life[0], marketVal, evec

def movingStd(y, length):
    std = [0]*len(y)
    for count, price in enumerate(y):
        if count>length:
            std[count]=np.std(y[count-int(length):count])
        else:
            std[count]=1
    return np.matrix(std)

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
