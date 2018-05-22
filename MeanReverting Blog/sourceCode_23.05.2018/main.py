import sys, getopt
from backtest import Backtest
from live import Live
def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'p:x:s:c:')                                       #feed in input from cmd
    except:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-p'):
            if arg.lower() in ['5m','15m','30m','1h','1d']:
                period = arg
            else:
                print('invalid period')
                sys.exit(2)
        if opt in ('-x'):
            if arg.lower() in ['poloniex','snp500']:
                exchange = arg
            else:
                print('invalid exchange')
                sys.exit(2)
        if opt in ('-s'):
            if arg.lower() in ['live','backtest']:
                state=arg
            else:   
                print('invalid state')
                sys.exit(2)
        if opt in ('-c'):
            if exchange == 'poloniex' and arg in ['BTC/USDT','OMG/BTC']:
                currencey=arg
            elif exchange == 'snp500' and arg in ['GOOG']:
                currencey = arg
            else:
                print('invalid currency for this exchange')
                sys.exit(2)

                
    #Data Directory:
    directory = 'C:/Users/Billy/Documents/Code/MeanRevertingStrategy/Data/'
    
    #BACKTESTING
    if state=='backtest':
        test_model = Backtest(exchange, currencey, period, directory)
        test_model.test_stationarity()

    #LIVE
    if state == 'live':
        model = Backtest(exchange, currencey, period, livePreScreen = True)                  #live pre screen makes sure the given curency is indeed stationary & returns the parameters of the model
##        if model.stationary == true:
##            while something
##                run mean reverting stragegy


        
if __name__=='__main__':

    main(sys.argv[1:])
