### Mean Reverting Trade Strategy

## 17/05/2018
The aim is to build a live platform that trades off a mean reverting strategy. To implement such a strategy, we need a stationary time series. All the time series that we deal with will not be stationary in their given form, so we must transform them. As is my other projects, I will be testing on bitcoin as its the omst readily available currencey that I have access to the data of. 

## ADF Test

First is the testing of stationarity. " If the hypothesis λ = 0 can be rejected, that means the next move Δy(t) depends on the current level y(t − 1)" - Ernie Chan. The test statistic for this is  λ/SE(λ), and is regressed on Δy(t) = λy(t − 1) + μ + βt + α1Δy(t − 1) + … + αkΔy(t − k) + ∋(t). When we run such a test on white noise, or on a sin plot for a set period, we know these periods are mean reverting and that λ!=0, so they are good test cases as proofs of concept.

Code:
```
from statsmodels.tsa.stattools import adfuller

def test_stationarity(ts):
    #results of ADF test
    adf = adfuller(ts, autolag='AIC')
    dfoutput = pd.Series(adf[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in adf[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)
    plt.show()
```
The time series analysis plots give insight into the autocorrelation (correlation of residuals) which we also require to not exist for a stationary series. (code from http://www.blackarbs.com/blog/time-series-analysis-in-python-linear-models-to-garch/11/1/2016):

```
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
```
<p align="center">
  <img src="whitenoise1ADF.png" width="350">
  <img src="sin1ADF.png" width="350">
</p>

As expected, both return test statistics << 1% confidence, so we can confidently reject the null that λ = 0 i.e. the series is mean reverting, at a rate proportional to λ. Carrying out the same test on prices of bitcoin at 5 minute ticks, however:

<p align="center">
  <img src="bitcoinADF.png" width="400">
</p>

i.e. with p = 0.8 we cannot reject the null so we can't say that the prices for bitcoin prices are mean reverting. I'll now venture in to Hurst Exponents - another test for a mean reverting time series.
##
##
## Hurst Exponent
Following a post on https://stackoverflow.com/questions/39488806/hurst-exponent-in-python, if H<0.5 the series is mean reverting, if H>0.5 it's trending. If H=0.5, its a geometric walk.
```
Dr Chan states that if z is the log price, then volatility, sampled at intervals of τ, is volatility(τ)=√(Var(z(t)-z(t-τ))). To me another way of describing volatility is standard deviation, so std(τ)=√(Var(z(t)-z(t-τ)))
std is just the root of variance so var(τ)=(Var(z(t)-z(t-τ)))
Dr Chan then states: In general, we can write Var(τ) ∝ τ^(2H) where H is the Hurst exponent
Hence (Var(z(t)-z(t-τ))) ∝ τ^(2H)
Taking the log of each side we get log (Var(z(t)-z(t-τ))) ∝ 2H log τ
[ log (Var(z(t)-z(t-τ))) / log τ ] / 2 ∝ H (gives the Hurst exponent) where we know the term in square brackets on far left is the slope of a log-log plot of tau and a corresponding set of variances.
```
Again our test cases will be the sin and white noise functions, where we'd expect a hurst exponent of 0 according to the above.Also for a geometric random walk, we expect H(randWalk)=0.5. Running the program for these cases we find H(white noise)=0.00128, H(sin) = 0.98756. Our hypothesis is met in the case of white noise, but not for the sin curve. This is because sin was only covering one period. Inputting a time series with ~100 periods, we et H(sin)~0.14, which as we expected is strongly mean reverting. Further, H(randWalk)=0.49984.... ~ 0.5 as expected and H(any linear function ax+b+w(t)) ~ 1.Now to test it on bitcoin prices, we find:

```
    H(bitcoin - 1hr - past 20 days) ~ 0.45
    H(bitcoin - 1hr - past 200 days) ~ 0.49
    H(buttcoin - 5m - past 17 days) ~ 0.45
    H(bitcon - 5m - past 1.7 days ~ 0.415
```
All of these indicate that the price of coin is weakly mean reverting in the short run and less so in the long run.
    
K so now we have our hurst exponents, we want to test their significance. This can be done by a variance ratio test to see if var(z(t)-z(t-tau))/(tau*(var(z(t)-z(t-1)))==1. Pretty much, we're trying to reject the null that H = 0.5 (which it would if the previous were satisfied as this would mean it's a random walk). For this, Im going to use the code I found on a quantopian discussion board:
```
def normcdf(X):
    (a1,a2,a3,a4,a5) = (0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429)
    L = abs(X)
    K = 1.0 / (1.0 + 0.2316419 * L)
    w = 1.0 - 1.0 / sqrt(2*pi)*exp(-L*L/2.) * (a1*K + a2*K*K + a3*pow(K,3) + a4*pow(K,4) + a5*pow(K,5))
    if X<0:
        w = 1.0-w
    return w
 
 
def vratio(a, lag = 2, cor = 'hom'):
    t = (std((a[lag:]) - (a[1:-lag+1])))**2;
    b = (std((a[2:]) - (a[1:-1]) ))**2;
 
    n = float(len(a))
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
 
    zscore = (vratio - 1) / sqrt(float(varvrt))
    pval = normcdf(zscore);
 
    return  vratio, zscore, pval
```
Again running this on a test case of white noise, we get "Variance Ratio Test: (0.4833121939238241, -16.33910306436103, 0.0)". As expected, this is telling us that there is a probability of 0 that this series DOES NOT has a hurst exponent of H = 0.48 ~ 0.5. Seems to be working as expected. Running it on 5m bitcoin prices for the last 5000 ticks, we retrieve H = 0.4564870082435933. This indicates that the price series is weakly mean reverting. Furthermore, when running the hurst exponent on the USDCAD data (as seen in Ernie Chan's book), we retrieve the same H=0.49 as ernie did. Wahoo.

## Half life of mean reversion
Doing some magical math (again see ernie chan's books) leads us to the fact that the half life of mean reversion is equal to ln(2)/lambda, where lambda is the coefeccient of the regression y(t)-y(t-1) vs y(t). This half life is neat because: ``` It determines a natural time scale for many parameters in our strategy. For example, if the half life is 20 days, we shouldn’t use a look-back of 5 days to compute a moving average or standard deviation for a mean-reversion strategy.```
All test cases are again passed (comparing to ernie's book with the same data we get the same value), so it's now time to implement a basic trading strategy to test the theory.

##  Linear trading strategy
The following is a strategy to highlight the POTENTIAL for profit, but is not an optimal trading strategy at all.
We simply seek to own a quantity of stock proportional to the negative normalised deviation from the moving average, with standard deviation given by a moving std:
    mVal = - (y-movingAve)/movingStd
For each tick, we sell the pervious shares and buy new shares at the new market value, so the profit/loss at time t is given by:
    PNL(t) = #unitsOwned * changeInPrice = mVal(y-1)(y(t)-y(t-1)/y(t-1), where y is the price at time t.

We implement the previous statistical tests to determine whether the series is indeed mean reverting - and if so find the hald life of mean reversion. We use this half life as our lookbacks in our moving average and standard deviations.
Plotting a cumulative distribtion plot of this data, we should get a graph representing the P&L over the given timeframe. The main testcase here is a comparison to Ernie Chan's book. Using the USDCAD data, we get the following test statistics and P&L:
<p align="center">
  <img src="PnLUSDCAD.png" width="800">
</p>
This is the exact same as the outcome in Ernie Chan's book so im hyped af rn. Using the same trading strategy on the price of bitcoin for 5 minute tickers (which we have already seen is weakly mean reverting), we recieve the profits:
<p align="center">
  <img src="PnLBTC.png" width="800">
</p>
cool stuff. I was accidentally reading a dataframe into the variance ratio test (instead of a list) hence the NAN's. The true result is (0.8809299369526877, -6.95414021910431, 1.7847945343874017e-12)

### Cointegration
As discussed in the early stages of this project, a price series is rarely stationary/ mean reverting on its own, however it is possible to construct a portfolio with certain hedges that are stationary. When we can create a stationary linear combination of non-stationary price series, the series' are cointegrated. (Hedge ratio = number of units longed/shorted for each asset). There are 2 main tests we'll explore for cointegration in price series: CADF and the Johansen test.

## CADF
When we do a linear regression of two price series, we'll retrieve a slope parameter describing linear correlation between them. THis value describes the hedge ratio of one asset against another, and if it's an accurate fit for a co-integrating pair of assets then the residuals of the fitted model (about this slope) should be stationary. Hence, we can run a adf test on the residuals of our model to test for co-integration. Doing so on the EWA-EWC (exchange traded funds) yields:
```
Test Statistic                   -3.163140
p-value                           0.022220
#Lags Used                        1.000000
Number of Observations Used    2223.000000
Critical Value (1%)              -3.433295
Critical Value (5%)              -2.862841
Critical Value (10%)             -2.567463
```
Hence, we are 95% certain that lambda != 0 i.e. the two series are cointegrated. I wanted to see if there was any co-integration bwtween bicoin and popular alt-coins as I always see negatively proportional changes in price in the crypto markets. The test resulted in:
```
Test Statistic                   -2.750362
p-value                           0.065721
#Lags Used                       14.000000
Number of Observations Used    4985.000000
Critical Value (1%)              -3.431662
Critical Value (5%)              -2.862120
Critical Value (10%)             -2.567079
```
According to this, the price series' are almost at the 5% level that mu!=0. This is a strong indication that our price series are cointegrated, but we can visualise it by plotting the residuals of the model:
<p align="center">
  <img src="cointegrationBTCXMR.png" width="500">
</p>
This shows the residuals bouncing around 0, this looks like a stationary curve and also looks like money.

    bitcoin = self.ts['Close'][-5000:]
    xmr = self.tsA['Close'][-5000:]
    plt.plot(bitcoin.values)
    plt.plot(omg.values)
    plt.show()
    xmr_Const = sm.add_constant(xmr.values) # we want to add a constant under the assumption that there can be a nonzero off set of the     pair portfolio’s price series
    model = sm.OLS(bitcoin.values,xmr_Const).fit()
    adf(model.resid)
    plt.plot(model.resid) 
    plt.show()

## Johansen Test
The johansen test is testing for stationarity in the matrix eqn:
```
ΔY(t) = BY(t − 1) + M + βt + A1ΔY(t − 1) + … + AkΔY(t − k) + ∋(t)
where B =  λ in vector form. We are testing if B=0
M,B,A all matrices
Y is a [len(ts) x n] matrix for n time series
```
let r = rank(B), which corresponds to the number of independent portfolios we can construct for the potentially cointegrated time series'. We are testing for the number of r, recieving confidences that r==0, r<=1, r<=2,... ,r<=n-1. This is found via 2 statistical tests, finding a trace and a eigen statistic. The math behind this is an exploration for a later date. The statsmodel module used to include a johansen test module, but it's been lost within other branches so I had to use a branch from a few years ago & convert to python3. Running the test on the EWCEWA data as in ernie chan's book, we retrieve:
```
--------------------------------------------------
--> Trace Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 17.568396088804985 13.4294 15.4943 19.9349
r = 1 t 4.851448253638874 2.7055 3.8415 6.6349
--------------------------------------------------
--> Eigen Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 12.716947835166113 12.2971 14.2639 18.52
r = 1 t 4.851448253638874 2.7055 3.8415 6.6349
--------------------------------------------------
eigenvectors:n [[ 0.5572649  -0.38211549]
 [-0.65401841  0.13409347]]
--------------------------------------------------
eigenvalues:n [0.00570685 0.00218099]
--------------------------------------------------
```
This indicates that we reject the null that there is less than 2 linear combos with 95% confidence by both the eigen and trace statistics. The linear combinations are given under the eigenvectors, with the corresponding eigenvalues.The eigenvalues are ordered high to low, with the highest corresponding to the "strongest" linear combo with the fastest mean reversion half life. The test can be carried out for n time series too, which I tested on the EWA, EWC and IGE ETF's:
```
--------------------------------------------------
--> Trace Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 32.2079137305541 27.0669 29.7961 35.4628
r = 1 t 16.683723355665077 13.4294 15.4943 19.9349
r = 2 t 5.384494123019343 2.7055 3.8415 6.6349
--------------------------------------------------
--> Eigen Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 15.524190374889017 18.8928 21.1314 25.865
r = 1 t 11.29922923264573 12.2971 14.2639 18.52
r = 2 t 5.384494123019343 2.7055 3.8415 6.6349
--------------------------------------------------
eigenvectors:n [[ 0.76975358  0.07167801  0.07225663]
 [-0.87789041 -0.82785766  0.24339546]
 [ 0.08870492  0.57532642 -0.07362409]]
--------------------------------------------------
eigenvalues:n [0.01032348 0.00752451 0.00359279]
--------------------------------------------------
```
Here, we find we have three cointegrating relations with >95% certainty. We want to implement a similar trading Linear trading strategy to test profit potential, so we need to compute the half life of mean reversion for our portfolio.

## Half life of mean reversion for cointegrated time series

The half life of mean reversion if found using the same method as found above, but this time we include a matrix marketVal which multiplies each time series element by the corresponding eigenvector value, to give the market value of the portfolio at every time according to our johansen test. This marketValue is equivalent to the linear combination optimisted by the johansen test, being calculated at each time 't'.

We then regress Y(t)-Y(t-1) vs the market value at time T, where Y is a Txn matrix including our 'n' time series, to retrieve the half life of mean reversion for a linear combination of our time series with the coefficients given by the eigenvectors from johansen test. (we use the first eigenvector as is corresponds to the shortest length of mean reversion).
```
def halfLife_coint(y, evec):
    marketVal = np.sum(np.multiply(repmat(evec,len(y[1]),1),y),1)
    deltaY = np.diff(marketVal,axis=0)
    yy = np.hstack([marketVal[1:],np.ones((len(marketVal[1:]),1))])
    beta = np.linalg.lstsq(yy, deltaY)
    half_life = log(2) / beta[0]
    return half_life[0], marketVal, evec
```
Running this on the EFT's of ewc, ewa and ige, we retrieve a half life of mean reverson of 25 days which isn't too far from ernie's 23 days. Im guessing this difference stems from differences in the data sets (different end and start points). It should be a point of investigation in the future however.
```
--------------------------------------------------
--> Trace Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 32.2079137305541 27.0669 29.7961 35.4628
r = 1 t 16.683723355665077 13.4294 15.4943 19.9349
r = 2 t 5.384494123019343 2.7055 3.8415 6.6349
--------------------------------------------------
--> Eigen Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 15.524190374889017 18.8928 21.1314 25.865
r = 1 t 11.29922923264573 12.2971 14.2639 18.52
r = 2 t 5.384494123019343 2.7055 3.8415 6.6349
--------------------------------------------------
eigenvectors:n [[-0.87789041 -0.82785766 -0.24339546]
 [ 0.76975358  0.07167801 -0.07225663]
 [ 0.08870492  0.57532642  0.07362409]]
--------------------------------------------------
eigenvalues:n [0.01032348 0.00752451 0.00359279]
--------------------------------------------------
[-0.87789041  0.76975358  0.08870492]
C:\Users\Billy\Documents\Code\MeanRevertingStrategy\backtest.py:103: FutureWarning: `rcond` parameter will change to the default of machine precision times ``max(M, N)`` where M and N are the input matrix dimensions.
To use the future default and silence this warning we advise to pass `rcond=None`, to keep using the old, explicitly pass `rcond=-1`.
  beta = np.linalg.lstsq(yy, deltaY)
Lookback:        [[25.25137904]]
```
Finding the half life on an Bitcoin / XMR / ETH integrated portfolio returns a half life of mean reversion of 16 days:
```
--------------------------------------------------
--> Trace Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 50.075369779754695 27.0669 29.7961 35.4628
r = 1 t 11.463537268052487 13.4294 15.4943 19.9349
r = 2 t 0.8046203273094117 2.7055 3.8415 6.6349
--------------------------------------------------
--> Eigen Statistics
variable statistic Crit-90% Crit-95%  Crit-99%
r = 0 t 38.61183251170221 18.8928 21.1314 25.865
r = 1 t 10.658916940743076 12.2971 14.2639 18.52
r = 2 t 0.8046203273094117 2.7055 3.8415 6.6349
--------------------------------------------------
eigenvectors:n [[ 0.00912317 -0.00274728  0.00064343]
 [-0.32772813  0.01344684 -0.04555705]
 [ 0.01828183  0.02547802 -0.0182097 ]]
--------------------------------------------------
eigenvalues:n [0.00769723 0.00213079 0.00016101]
--------------------------------------------------
C:\Users\Billy\Documents\Code\MeanRevertingStrategy\backtest.py:102: FutureWarning: `rcond` parameter will change to the default of machine precision times ``max(M, N)`` where M and N are the input matrix dimensions.
To use the future default and silence this warning we advise to pass `rcond=None`, to keep using the old, explicitly pass `rcond=-1`.
  beta = np.linalg.lstsq(yy, deltaY)
Lookback:        [[16.46577736]]
```
Take note that the eigenvector here is [ 0.00912317 -0.32772813  0.01828183]. Make sure you don't confuse the output of the johansen test & accidentally take a row as the eigenvector.

## Linear trading srtategy
We observe the same method here as in the case of one series. he algorithm works as follows, (it might be a bit tricky to wrap your head around first):
Again, from a quantopian blog:
```
The total worth of the portfolio at time t is marketValue, which is the sum of each position multiplied with its equivalent value from the first column of the eigenvector from the Johansen test.
numUnits is the negative z-score of the total worth of the portfolio with a lookback period equal to the half-life of the mean reversion. The z-score tells you how many standard deviations you are away from the mean.
We then multiply the z-score with the assignment according to Johansen (AA*BB) and get the worth of the portfolio which give us the positions which we have entered.
Now we multiply the position values with the change in price and divide that by the previous day’s price to give us the profit/loss at time t.
You can see that the strategy continuously enters and exits, which is not a realistic assumption. However, according to Chan, this will give a valid indication whether a strategy might be worth pursuing in the first place.
```
Corresponding to the code:
```
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
```
We can now visualise potential profits in a simple mean reverting strategy for a cointegrated time series. For the ETF's in the above examples, the plot of returns vs time is:
<p align="center">
  <img src="ETF's.png" width="800">
</p>
For the btc/eth/xmr cointegrated series, the returns for 5m ticker data are:
<p align="center">
  <img src="btcethxmr.png" width="800">
</p>
For the btc/eth/xmr cointegrated series, the returns for 30m ticker data are:
<p align="center">
  <img src="btcethxmr1.png" width="800">
</p>
For the btc/eth/xmr cointegrated series, the returns for 31d ticker data are:
<p align="center">
  <img src="btcethxmr2.png" width="800">
</p>
