import pandas as pd
import talib
import numpy as np
import time
from math import floor, isnan
class MLstrategy(object):

	def __init__(self, data, currencies, model_directory, pip):
		self.data = data
		self.currencies = currencies
		self.model_directory = model_directory
		self.pip = pip

	#pretty much just adding a fuck ton of features and seeing what that booty do
	def preprocessIndicators(self, forecastLen):
		close_columns = [col for col in list(self.data.columns.values) if 'Close' in col]
		open_columns = [col for col in list(self.data.columns.values) if 'Open' in col]
		high_columns = [col for col in list(self.data.columns.values) if 'High' in col]
		low_columns = [col for col in list(self.data.columns.values) if 'Low' in col]

		#features dependent only on the closing price
		sma_lengths = [16,64,256]
		for currency in close_columns:
			#no length dependence #add HT_TRENDLINE - Hilbert transform whatever the fuck that is
			self.data[currency+'_HT_TRENDLINE_'] = talib.HT_TRENDLINE(self.data[currency])
			
			for length in sma_lengths:
				#add SMA column
				self.data[currency+'_SMA_'+str(length)] = talib.SMA(self.data[currency], timeperiod = length)
				#add WMA - weighted moving average
				self.data[currency+'_WMA_'+str(length)] = talib.WMA(self.data[currency], timeperiod = length)
				#add TRIMA - triangilar moving average
				self.data[currency+'_TRIMA_'+str(length)] = talib.TRIMA(self.data[currency], timeperiod = length)
				#add TEMA -  triple exponential moving average
				self.data[currency+'_TEMA_'+str(length)] = talib.TEMA(self.data[currency], timeperiod = length)
				#add DEMA - double exp ma
				self.data[currency+'_DEMA_'+str(length)] = talib.DEMA(self.data[currency], timeperiod = length)
				#add bollinger bands
				upperband, middleband, lowerband = talib.BBANDS(self.data[currency], timeperiod=length, nbdevup=2, nbdevdn=2, matype=0)
				self.data[currency+'_BOLLINGER_UPPER_'+str(length)] = upperband
				self.data[currency+'_BOLLINGER_MIDDLE_'+str(length)] = middleband
				self.data[currency+'_BOLLINGER_LOWER_'+str(length)] = lowerband


			#we also want to add a 'forecast column', which has the column value for a specific row 'forecastLen' units in the future.
			self.data[currency+'_FORECAST_'+str(forecastLen)] = self.data[currency].shift(-forecastLen)
			self.data[currency+'_pipDiff_'+str(forecastLen)]=list(map(self.classify, self.data[currency], self.data[currency+'_FORECAST_'+str(forecastLen)]))


		return self.data

	#the pip is a unit to show how much higher/lower the price is
	#for starters, if the diff is <0, we return 0, and if >0, we return the number of pips in which its higher
	def classify(self,current,future):
		diff = future-current
		if isnan(diff):
			return 0
		elif diff<0:
			return 0
		elif diff > 0 and diff <= self.pip:
			return 1
		elif diff > self.pip and diff <=2*self.pip:
			return 2
		elif diff > self.pip and diff <=3*self.pip:
			return 3	
		elif diff > self.pip and diff <=4*self.pip:
			return 4
		elif diff > self.pip and diff <=5*self.pip:
			return 5
		else:
			return 0



		