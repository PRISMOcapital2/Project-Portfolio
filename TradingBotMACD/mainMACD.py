from getdata import GetData
from strategy import Strategy
from graphics import Graphics

def main():
    data = GetData('poloniex',newdata=True)
    tickers = ['LTC/USDT']#,'BTC/USDT']                           #tickers = data.tickers()
##    tickers = ['OMG/BTC']#,'ETH/BTC','XMR/BTC','ZEC/BTC','BTC/USDT']
    periods = ['5m','15m','30m','1h']                               #periods = ['5m','15m','30m','1h']
    maximum_parameters = []
    proportion_test = 0.1
    graph_results = True
    data.fetch('BTC/USDT') # use if list length error'ETH/USDT','XRP/USDT',
    type_coin = 'USDT'
    for tick in tickers:
        if tick[-len(type_coin):]==type_coin:
            data.fetch(tick)
            temp_results = []
            for numsimul in [1,2,3,4,5,6,7,8,9,10]:
                for period in periods:
                    '''formats the bitcoin and current coin data to the right period'''
                    tick_data = data.periodFormatter(tick,period)
                    startDate = tick_data.index[0]
                    btc_data = data.periodFormatter('BTC/USDT',period,startDate)
                    
                    '''formats the raw data to the proportion of data chosen'''
                    startDate = tick_data.index[int((1-proportion_test)*len(tick_data))]
                    endDate = tick_data.index[-1]
                    btc_prices = btc_data.loc[startDate:endDate]['Close']
                    tick_prices = tick_data.loc[startDate:endDate]['Close']

                    if len(tick_prices)!=len(btc_prices):
                        tick_prices.drop(tick_prices.index[0],inplace=True)
                    
                    if len(tick_prices)==len(btc_prices) or tick[-len(type_coin):]==type_coin:
                        
                        strategy = Strategy(len(tick_prices),numsimul)
                        
                        for count, price in enumerate(tick_prices.values):
                            if type_coin=='BTC':
                                strategy.tick(price, btc_prices.values[count])
                            elif type_coin == 'USDT':
                                strategy.tick(price)
                            strategy.macd(26,12,9,count, len(tick_prices))
                        temp_results.append([tick, period, strategy.profit, strategy.balance, tick_prices, strategy.numtrades,min(strategy.balanceList),strategy])
                        
                    else:
                        print('length error')
                        break

            optimumParam = None
            for result in temp_results:
                if optimumParam==None:
                    optimumParam=result
                    optimum = result
                elif result[3]>optimumParam[3]:
                    optimumParam = result
                else:
                    pass

            print(optimumParam[0],optimumParam[1],'\nProfit on one coin per trade:',optimumParam[2],'\nBalance on',optimumParam[-1].USDpertrade,'USD per trade:',optimumParam[3],
                  '\nNumber of simeltaneuos trades:',optimumParam[-1].numSimul,'\nNumber of trades:',optimumParam[-1].numtrades)
            maximum_parameters.append(optimumParam)
    for param in maximum_parameters:
        plot = Graphics(param[4],bal=param[-1].balanceList, buylist = param[-1].buylist, selllist = param[-1].selllist,MACD = param[-1].MACD, signal=param[-1].signal, EMAfast = param[-1].EMAfast, EMAslow = param[-1].EMAslow)
        plot.MACD_plot(26)

if __name__=='__main__':
    main()
