from getdata import GetData
from strategy import Strategy
from graphics import Graphics

def main():
    data = GetData('poloniex',newdata=False)
    tickers = ['OMG/BTC']                           #tickers = data.tickers()
    periods = ['30m']                               #periods = ['5m','15m','30m','1h']
    maximum_parameters = []
    proportion_test = 0.1
    graph_results = True
                                                    #data.fetch('BTC/USDT') # use if list length error
    
    for tick in tickers:
        if tick[-3:]=='BTC':
            data.fetch(tick)
            temp_results = []
            
            for period in periods:
                '''formats the bitcoin and current coin data to the right period'''
                tick_data = data.periodFormatter(tick,period)
                startDate = tick_data.index[0]
                btc_data = data.periodFormatter('BTC/USDT',period,startDate)
                prices = [close for close in tick_data['Close']]
                
                '''formats the raw data to the proportion of data chosen'''
                startDate = tick_data.index[int((1-proportion_test)*len(prices))]
                endDate = tick_data.index[-1]
                btc_prices = btc_data.loc[startDate:endDate]['Close']
                tick_prices = tick_data.loc[startDate:endDate]['Close']

                for MAlong in [10,15,30]:
                    for x in [2,3,4]:
                        MAshort = int(MAlong/x)
                        if len(tick_prices)==len(btc_prices):
                            
                            strategy = Strategy(len(tick_prices))
                            
                            for count, price in enumerate(tick_prices.values):
                                strategy.tick(price, btc_prices.values[count])
                                strategy.movingaverage(MAlong, MAshort, count)

                            profit, balance = strategy.returnParam()
                            temp_results.append([tick, period,tick_prices, strategy, profit, balance, MAlong, MAshort])
                        else:
                            print('length error')
                            break
                        
            optimumParam=None
            for result in temp_results:
                if optimumParam==None:
                    optimumParam=result
                    optimum = result
                elif result[5]>optimumParam[5]:
                    optimumParam = result
                else:
                    pass
                
            print(optimumParam[0],optimumParam[1],optimumParam[4],optimumParam[5],optimumParam[6],optimumParam[7])
            maximum_parameters.append(optimumParam)
            
        for param in maximum_parameters:
            plot = Graphics(param[2],param[3].MAlong,param[3].MAshort,param[3].buylist,param[3].selllist, param[3].balanceList)                                 
            plot.MA_plot()
         
                            
                        
if __name__=='__main__':
    main()
