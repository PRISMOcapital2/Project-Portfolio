import pandas as pd
import matplotlib.pyplot as plt
import datetime as df
import time
class Graphics(object):

    def __init__(self, rawdf, MAlistL=None, MAlistS=None, buylist=None, selllist=None, bal=None, MACD = None, signal = None, EMAfast = None, EMAslow = None):
        self.df = rawdf
        self.MAlong = MAlistL
        self.MAshort = MAlistS
        self.buy = buylist
        self.sell = selllist
        self.bal = bal

        self.MACD = MACD
        self.signal = signal
        self.fast = EMAfast
        self.slow = EMAslow

        self.df.index = pd.to_datetime(self.df.index,unit='ms')
    def MA_plot(self):
##        print(len(self.df),len(self.MAlong),len(self.MAshort))
        try:
            MAlong = pd.Series(self.MAlong, index = self.df.index)
            MAshort = pd.Series(self.MAshort, index = self.df.index)
        except Exception as e:
            self.df = self.df.drop([self.df.index[0]])
            MAlong = pd.Series(self.MAlong, index = self.df.index)
            MAshort = pd.Series(self.MAshort, index = self.df.index)
            
        df_open = pd.DataFrame(self.df[self.buy])
        df_close = pd.DataFrame(self.df[self.sell])
        
        fig, axes = plt.subplots()
        MAlong.plot()
        MAshort.plot()
        self.df.plot(color='black',linewidth=0.3)
        plt.scatter(df_open.index,df_open.Close,marker='^',color='green')
        plt.scatter(df_close.index,df_close.Close,marker='v',color='red')
##        print(self.bal,self.df.values)
        for count, balance in enumerate(self.bal):
            if self.sell[count]==True:
                axes.annotate(str(balance),(self.df.index[count],self.df.values[count]))
        plt.show()

    def MACD_plot(self,startMACD):
        MACD = pd.Series(self.MACD, index = self.df.index[startMACD:])
        signal = pd.Series(self.signal,index=self.df.index[startMACD:])
        
        fast = pd.Series(self.fast, index = self.df.index[startMACD:])
        slow = pd.Series(self.slow,index=self.df.index[startMACD:])
        df_timeadj = pd.DataFrame(self.df[startMACD:])
        df_open = pd.DataFrame(df_timeadj[self.buy])
        df_close = pd.DataFrame(df_timeadj[self.sell])
        
        fig, axes = plt.subplots(nrows = 2, ncols = 1,sharex=True)
        axes[0].plot(self.df.index,self.df.values,color='black',linewidth=0.6, label='Price')
        axes[0].plot(fast.index,fast.values,label='Fast EMA',linewidth=0.3)
        axes[0].plot(slow.index, slow.values,label = 'Slow EMA',linewidth=0.3)
        axes[0].legend()
        axes[0].scatter(df_open.index,df_open.Close,marker='^',color='green')
        axes[0].scatter(df_close.index,df_close.Close,marker='v',color='red')
        axes[1].plot(signal.index,signal.values, label = 'Signal')
        axes[1].plot(MACD.index,MACD.values, label = 'MACD 9 day EMA')
        axes[1].scatter(df_open.index,signal.values[self.buy],marker='^',color='green')
        axes[1].scatter(df_close.index,signal.values[self.sell],marker='v',color='red')
        axes[1].legend()
        fig.autofmt_xdate()
        for count, balance in enumerate(self.bal):
            if self.sell[count]==True: #or self.buy[count]==True:
                axes[0].annotate(str(balance),(self.df.index[startMACD+count],self.df.values[startMACD+count]))
       

        
        plt.show()
