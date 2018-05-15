import os
import pickle
import pandas as pd
import ccxt
import bs4 as bs
import requests
import datetime as dt
import os
import pandas_datareader.data as web
from indicators import Indicators
import math
class GetData(object):
    
    def __init__(self,exchange,newdata=False):
        self.exchange = exchange
        self.newdata = newdata
        self.directory = 'C:/Users/Billy/Documents/Code/ML_trends/'
        if self.exchange == 'poloniex':
            self.exchangeObject = exchangeObject(self.exchange)
            
    def tickers(self):
        if os.path.isfile(self.directory+'Ticker_data/'+self.exchange+'_tickers.pickle'):
            tickers = dePickler(self.directory+'Ticker_data/'+self.exchange+'_tickers.pickle')
        else:
            if self.exchange == 'poloniex':
                self.exchangeObject.load_markets()
                tickers = list(self.exchangeObject.markets.keys())
                pickler(self.directory+'Ticker_data/'+self.exchange+'_tickers.pickle',tickers)
            elif self.exchange == 'snp500':
                resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
                soup = bs.BeautifulSoup(resp.text)
                table = soup.find('table', {'class':'wikitable sortable'})
                tickers = []
                for row in table.findAll('tr')[1:]:
                    ticker = row.findAll('td')[0].text
                    tickers.append(ticker)
                pickler(self.directory+'Ticker_data/'+self.exchange+'_tickers.pickle',tickers)
        self.tickers = tickers
        return tickers


    def fetch(self, ticker):
        if self.exchange == 'poloniex':
                                                                            #ticker in format 'BTC_OMG'
                                                                            #period in format '5m', '1h' etc
                                                                            #downloads all data for a given exchange
            directory = self.directory+'Data/Raw_data/'+self.exchange+'/5m/'+tickDir(ticker)+'.pickle'
            if (not os.path.isfile(directory)) or self.newdata==True:
                data = self.exchangeObject.fetch_ohlcv(ticker, timeframe = '5m')
                df = pd.DataFrame(data)
                df.columns = ['Date','Open','High','Low','Close','Volume']
                df.set_index('Date',inplace=True)
                if not os.path.exists('C:/Users/Billy/Documents/Code/ML_trends/Data/Raw_data/'+self.exchange+'/5m'):
                    os.makedirs('C:/Users/Billy/Documents/Code/ML_trends/Data/Raw_data/'+self.exchange+'/5m')
                pickler(directory, df)
                return df
                
            elif os.path.isfile(directory):
                return dePickler(directory)
            
        if self.exchange == 'snp500':
            directory = self.directory+'Data/Raw_data/'+self.exchange+'/1d/'+ticker+'.pickle'
            if not os.path.isfile(directory):
                df = web.DataReader(ticker,'google')
                if not os.path.exists('C:/Users/Billy/Documents/Code/ML_trends/Data/Raw_data/'+self.exchange+'/1d'):
                    os.makedirs('C:/Users/Billy/Documents/Code/ML_trends/Data/Raw_data/'+self.exchange+'/1d')
                pickler(directory, df)
                
            elif os.path.isfile(directory):
                return dePickler(directory)
            
                    

    def indicators(self, ticker):
        if self.exchange == 'poloniex':
            directory = self.directory+'Data/Raw_data/'+self.exchange+'/5m/'+tickDir(ticker)+'.pickle'
            data = dePickler(directory)
        else:
            data = dePickler(self.directory+'Data/Raw_data/'+self.exchange+'/1d/'+ticker+'.pickle')
        indicator_data = Indicators(data)
        for count, close in  enumerate(data['Close']):
            indicator_data.tick(close)

        percentages = pd.Series(indicator_data.percentChangelist)
        SMA = pd.Series(indicator_data.SMAlist)
        EMAslow = pd.Series(indicator_data.EMAslow)
        EMAfast = pd.Series(indicator_data.EMAfast)
        MACD = pd.Series(indicator_data.MACD)
        Signal = pd.Series(indicator_data.signal)
        smaDiff = pd.Series(indicator_data.smaDiff)

        data['PercentChange']=percentages.values
        data['SMA']=SMA.values
        data['EMAslow']=EMAslow.values
        data['EMAfast']=EMAfast.values
        data['MACD']=MACD.values
        data['Signal']=Signal.values
        data['SmaDiff']=smaDiff.values

        

        if self.exchange == 'poloniex':
            directory = self.directory+'Data/Raw_data/'+self.exchange+'/5m/'+tickDir(ticker)+'.pickle'
            pickler(directory,data)
        else:
            pickler(self.directory+'Data/Raw_data/'+self.exchange+'/1d/'+ticker+'.pickle',data)
       

        return data
                
                
        
    def periodFormatter(self, ticker, period,startDate=False):
        directory = self.directory+'Data/Raw_data/'+self.exchange+'/1d/'+tickDir(ticker)+'.pickle'

        if period == '5m':
            return dePickler(directory)
        
        else:
            if os.path.exists(self.directory+'Data/Raw_data'+'/'+self.exchange+'/'+period):
                pass
            else:
                os.makedirs(self.directory+'Data/Raw_data/'+self.exchange+'/'+period)
                        
            df_temp = dePickler(directory)
            if startDate != False:
                df_temp = df_temp.loc[startDate:]
                
            if period == '10m':
                df = df_temp.iloc[::2]
            elif period == '15m':
                df = df_temp.iloc[::3]
            elif period == '30m':
                df = df_temp.iloc[::6]
            elif period == '1h':
                df = df_temp.iloc[::12]
            elif period == '1d':
                df = df_temp.iloc[::288]
                
            pickler(self.directory+'PROJECT_1/Data/Raw_data/'+self.exchange+'/'+period+'/'+tickDir(ticker)+'.pickle',df)       

            return df


    
def exchangeObject(exchange_in):
    exchanges = [ccxt.acx(),ccxt.bitbay(),ccxt.bitfinex(),ccxt.bitflyer(),ccxt.bithumb(),ccxt.bitlish(),ccxt.bitmarket(),ccxt.bitmex(),ccxt.bitso(),
                             ccxt.bitstamp(),ccxt.bitstamp1(),ccxt.bittrex(),ccxt.bl3p(),ccxt.bleutrade(),ccxt.btcbox(),ccxt.btcchina(),ccxt.btcexchange(),ccxt.btcmarkets(),ccxt.btctradeua(),ccxt.btcturk(),
                             ccxt.btcx(),ccxt.bxinth(),ccxt.ccex(),ccxt.cex(),ccxt.chbtc(),ccxt.chilebit(),ccxt.coincheck(),ccxt.coinfloor(),ccxt.coingi(),ccxt.coinmarketcap(),ccxt.coinmate(),
                             ccxt.coinsecure(),ccxt.coinspot(),ccxt.cryptopia(),ccxt.dsx(),ccxt.exmo(),ccxt.flowbtc(),ccxt.foxbit(),ccxt.fybse(),ccxt.fybsg(),ccxt.gatecoin(),ccxt.gateio(),ccxt.gdax(),
                             ccxt.gemini(),ccxt.getbtc(),ccxt.hitbtc(),ccxt.huobi(),ccxt.huobicny(),ccxt.independentreserve(),ccxt.itbit(),ccxt.jubi(),ccxt.kraken(),ccxt.kucoin(),
                             ccxt.kuna(),ccxt.lakebtc(),ccxt.liqui(),ccxt.livecoin(),ccxt.luno(),ccxt.mercado(),ccxt.mixcoins(),ccxt.nova(),ccxt.okcoincny(),ccxt.okcoinusd(),ccxt.okex(),ccxt.paymium(),
                             ccxt.poloniex(),ccxt.qryptos(),ccxt.quadrigacx(),ccxt.southxchange(),ccxt.surbitcoin(),ccxt.therock(),ccxt.tidex(),ccxt.urdubit(),ccxt.vaultoro(),ccxt.vbtc(),
                             ccxt.virwox(),ccxt.wex(),ccxt.xbtce(),ccxt.yobit(),ccxt.yunbi(),ccxt.zaif(),ccxt.zb()]
 
    
    for count, exchange in enumerate([str(x) for x in exchanges]):
        if exchange_in.lower() in exchange:
            return exchanges[count]
            break
def pickler(directory, data):
    pickle_out = open(directory,'wb')
    pickle.dump(data,pickle_out)
    pickle_out.close()
    
def dePickler(directory):
    pickle_in = open(directory,'rb')
    return pickle.load(pickle_in)

def tickDir(ticker):
    #makes the ticker a save-able format
    if '/' in ticker:
        dex = ticker.find('/')
        return ticker[:dex]+'_'+ticker[dex+1:]

    
