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
Again our test cases will be the sin and white noise functions, where we'd expect a hurst exponent of 0 according to the above.Also for a geometric random walk, we expect H(randWalk)=0.5. Running the program for these cases we find H(white noise)=0.00128, H(sin) = 0.98756. Our hypothesis is met in the case of white noise, but not for the sin curve. This is because sin was only covering one period. Inputting a time series with ~100 periods, we et H(sin)~0.14, which as we expected is strongly mean reverting. Further, H(randWalk)=0.49984.... ~ 0.5 as expected and H(any linear function ax+b+w(t)) ~ 1.
```
Now to test it on bitcoin prices, we find:
    H(bitcoin - 1hr - past 20 days) ~ 0.45
    H(bitcoin - 1hr - past 200 days) ~ 0.49
    H(buttcoin - 5m - past 17 days) ~ 0.45
    H(bitcon - 5m - past 1.7 days ~ 0.415
```
All of these indicate that the price of coin is weakly mean reverting in the short run and less so in the long run.
    
