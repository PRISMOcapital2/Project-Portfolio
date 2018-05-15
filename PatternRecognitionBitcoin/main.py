from backtest import Backtest
import sys, getopt
def main(argv):
    #ENTER SOME VARIABLES   -x exchange <poloniex, snp500>
    #                       -s test type <live, backtest>
    #                       -l length of sublists
    #                       -v find variance of sublists for each variable <t,f>
    #                       -n new data <t,f>
    #                       -g graph <t,f>

    graph = False
    newdata = False
    findVar = False
    length = 30
    
    try:
        opts, args = getopt.getopt(argv,'hp:s:l:v:n:g:x:',)

    except getopt.GetoptError:
        sys.exit(2)
        
    for opt,arg in opts:
        if opt == 'h':
            print('trading-bot.py -p <period> -l <live/backtest>')
            sys.exit()
            #if -p followed by time period, sets the variable         
        if opt in ('-s','--state'):
            state = arg
        if opt in ('-x','--exchange'):
            exchange = arg
        if opt in ('-l','--length'):
            length = arg
        if opt in ('-n','--newdata'):
            newdata = arg
            if newdata.lower() == 't':
               newdata = True
            else:
                newdata=False
        if opt in ('-g','--graph'):
            graph = arg
            if graph.lower() == 't':
               graph = True
            else:
                graph = False
        

    
            
    if state.lower() == 'backtest':
        #FINDS PATTERNS
        patterns = Backtest(length, graph, newdata)
        patterns.find(exchange)
            

    if state.lower()=='live':
        pass
##        live stuff

if __name__=='__main__':
    main(sys.argv[1:])
