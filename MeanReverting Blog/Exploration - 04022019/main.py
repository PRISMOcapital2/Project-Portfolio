import sys, getopt
from getdata import GetData
import time
import pandas as pd
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import pickle
from mlstrategy import MLstrategy
import json


#this contains credentials, allowed currencies, exchanges etc. 
from credentials import *
'''
python main.py -x poloniex -p 5m -d False -c OMG/BTC,LTC/BTC,ZEC/BTC,DASH/BTC,ETH/BTC -a cryptocurrency -f D:\Machine_learning_finance\raw_data\period_5m_pulledAt_1546081156__OMG_BTC_LTC_BTC_ZEC_BTC_DASH_BTC_ETH_BTC_2018-12-29T105500000000000_to_2015-08-08T051000000000000.pickle
'''
def main(argv):
	
	#gets data, creates indicators. See mlstrategy to see the indicators.
	def data():
		#read in config info from json file
		data_config = json.load(open('input_config.json','r'))

		previous_data_name = data_config["data_and_directories"]["previous_data_name"]
		main_src_directory = data_config["data_and_directories"]["main_src_directory"]
		data_directory = data_config["data_and_directories"]["main_data_directory"]

		period = data_config["data_information"]["period"]
		assetType = data_config["data_information"]["asset_type"]
		pip = data_config["data_information"]["pip"]


		#we want to make it s.t. if the 'newdata' param is False, then there must be an accompanying file directory
		if data_config["data_and_directories"]["newData"]==False and previous_data_name == False:
			print('\nyou need to input a directory for the chosen file dummboy')
			sys.exit(2)

		#creating a very specific directory
		temp_dir = ''
		for currency in data_config["data_information"]["currencies"].split(','):
			temp_dir = temp_dir + '_' + tickDir(currency)	
			
		#get data for all specified tickers. NOTE as is, this will only create a df as long as the shortest time series
		if data_config["data_and_directories"]["newData"] == False:
			full_df = dePickler(data_directory + previous_data_name)
			temp_dir = 'period_' + str(period) + '_pulledAt_' + str(time.time())[:10] + '_' + temp_dir + '_' + str(full_df.index.values[-1]).replace('.','').replace(':','').replace(':','') + '_to_' + str(full_df.index.values[0]).replace('.','').replace(':','').replace(':','')  + '.pickle'

		else:
			dataObj = GetData(
				exchange = data_config["data_information"]["exchange"],
				directory = data_directory, 
				period = data_config["data_information"]["period"],
				asset_type = data_config["data_information"]["asset_type"], 
				newdata = data_config["data_and_directories"]["newData"])
			full_df = None

			#for each currency, fetch the time series and create a full dataframe
			for currency in data_config["data_information"]["currencies"].split(','):
				data = dataObj.fetch(currency)	

				#make the df include seperate names for open high low and close
				for label in ['Close','Open','High','Low','Volume']:
					if full_df is None:
						full_df =pd.DataFrame(data[label])
						full_df.columns = [currency+'_'+label]
					else:
						full_df[currency+'_'+label] = data[label]

			temp_dir = 'period_' + str(period) + '_pulledAt_' + str(time.time())[:10] + '_' + temp_dir + '_' + str(full_df.index.values[-1]).replace('.','').replace(':','').replace(':','') + '_to_' + str(full_df.index.values[0]).replace('.','').replace(':','').replace(':','')  + '.pickle'
		

		#create features for all of the data and save
		print('Creating Features')
		mlObj = MLstrategy(
			data = full_df, 
			currencies = data_config["data_information"]["currencies"].split(','), 
			model_directory =  main_src_directory+'models/',
			pip = pip
			)

		#if we're not collecting new data, then no need to create new data. Otherwise, create new features
		if data_config["data_and_directories"]["newData"]==False:
			df=full_df
		else:
			df = mlObj.preprocessIndicators(
				forecastLen = data_config["data_information"]["forecastLen"]
			)
			pickler(data_directory+'INDICATORS_ADDED_'+temp_dir, df)


		print(full_df)
		return full_df

	df = data()
	print(df.columns)
	# model_config = 

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
    else:
        return ticker


#runs main with input from cmd
if __name__=='__main__':
	main(sys.argv[1:])
