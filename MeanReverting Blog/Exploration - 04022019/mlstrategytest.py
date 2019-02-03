import pandas as pd
import talib
import numpy as np
import time
class MLstrategy(object):

	def __init__(self, data, currencies, model_directory):
		self.data = data
		self.currencies = currencies
		self.model_directory = model_directory

	#pretty much just adding a fuck ton of features and seeing what that booty do
	def preprocessIndicators(self, forecastLen):
		close_columns = [col for col in list(self.data.columns.values) if 'Close' in col]
		open_columns = [col for col in list(self.data.columns.values) if 'Open' in col]
		high_columns = [col for col in list(self.data.columns.values) if 'High' in col]
		low_columns = [col for col in list(self.data.columns.values) if 'Low' in col]

		#features dependent only on the closing price
		sma_lengths = [16]
		for currency in close_columns:
			
			for length in sma_lengths:
				#add SMA column
				self.data[currency+'_SMA_'+str(length)] = talib.SMA(self.data[currency], timeperiod = length)
				
			#we also want to add a 'forecast column', which has the column value for a specific row 'forecastLen' units in the future.
			#For starters, i'm going to use the 64 unit SMA as the forecast for stability in the prediction.
			self.data[currency+'_FORECAST_'+str(forecastLen)] = self.data[currency+'_SMA_16'].shift(-forecastLen)




		return self.data