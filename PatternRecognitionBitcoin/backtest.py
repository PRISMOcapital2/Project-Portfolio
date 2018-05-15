from getdata import GetData
import time
import matplotlib.pyplot as plt
import random
import multiprocessing
from sublists import SubLists
from patternrecognition import patternRecognition
from graphics import Grapher
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt

class Backtest(object):
    def __init__(self, length=30, graph = False, newdata=False):
        self.graph = graph
        self.newdata = newdata
        self.length = length

        
    def find(self, exchange):
        length = self.length
        variables = ['Close','Volume','MACD']
        parameters = [0.35, 60, 100]

        previousTestNumber = dePickler('C:/Users/Billy/Documents/Code/ML_trends/Draft_6/testNumberStore.pickle')
        currentTestNumber = previousTestNumber+1
        print(currentTestNumber)
        pickler('C:/Users/Billy/Documents/Code/ML_trends/Draft_6/testNumberStore.pickle',currentTestNumber)
        
        
        if self.graph != True:
            data = GetData('poloniex', self.newdata)
##            tickers = data.tickers()
            tickers = ['BTC/USDT']
            for tick in tickers:

                #FETCHES DATA FROM DATA MODULE
                start = time.time()
                data.fetch(tick)
                end = time.time()
                print('Time:\nFetching Data:',end-start)

                #USING THE INDICATOR MODULE, CREATES ARRAY WITH INDICATORS
                start = time.time()
                df = data.indicators(tick)
                end = time.time()
                print('Creating Indicators:',end-start)

                #start with first variable, go through and look for all the patterns you can find. now add another variable, and see if the pattern is there for this too.
                #also use incramentally decreasing parameter sizes.
                
                for numberOfParam in range(len(parameters)):
                    parameter = parameters[numberOfParam]
                    variable = variables[numberOfParam]
                    print(parameter, variable)
                    
                    #CREATES SUBLISTS TO BE MATCHED
                    maxStopIndex = int(20*len(df['Close'].values)/20)-30-length
                    startIndex =  int(15*len(df['Close'].values)/20)
                    
                    start = time.time()
                    length = 30
                    sublistsObj = SubLists(df, length, tick, 'poloniex', True, variable)      
                    prevAr = sublistsObj.returnLists(startIndex, maxStopIndex)          #prevAr = sublistArray
                    indexAr = sublistsObj.indexAr                                       #indexAr = [index1, index2, ....]   #index of element at end of pattern_i
                    end = time.time()                                                   #sublistArray = [self.prevListMaker(var1),self.prevListMaker(var2),...]
                    print('Creating Sublists:',end-start)                               #self.prevListMaker(var1) = [patternAr, outcomeAr]
                                                                                        #patternAr = [pattern_1, pattern_2, pattern_3, ...], pattern_i is a list
                                                                                        #outcomeAr = [outcome_1, outcome_2, ....]            outcome_i is a scalar    

                    if numberOfParam == 0:
                        n = 250
                        listPatterns = []
                    else:
                        listPatterns = dePickler('C:/Users/Billy/Documents/Code/ML_trends/Data/Patterns/recognisedPattern'+variables[numberOfParam-1]+str(currentTestNumber)+'.pickle')
                        n = len(listPatterns)
                        
                    aveLen = 10000
                    prevLen = 0
                    ratioDecrease = 0.7
                    loop = True

                    if numberOfParam!=0:
                        counter = 0
                        while loop==True:
                            recognisedPatternAr = findPatterns(n, variable, parameter, startIndex, maxStopIndex, listPatterns, df, length, indexAr, prevAr, numberOfParam, sublistsObj, variables, currentTestNumber)
                            if counter==0:
                                prevLen = len(recognisedPatternAr)
                            if len(recognisedPatternAr)>0  : 
                                lengths = []
                                for count, patt in enumerate(recognisedPatternAr):
                                    lengths.append(len(patt[0]))
                                baseLength = max(lengths)
                                aveLen = sum(lengths)/len(recognisedPatternAr)


                                if len(recognisedPatternAr)>int(ratioDecrease*prevLen) and aveLen>0.7*baseLength:
                                    baseLength = 0.7*baseLength
                                    parameter=parameter*0.7
                                    prevLen = len(recognisedPatternAr)
                                else:
                                    loop=False
                            else:
                                loop=False
                            counter+=1
                            
                        parameters[numberOfParam]=parameter
                    else:
                        recognisedPatternAr = findPatterns(n,variable, parameter, startIndex, maxStopIndex, listPatterns, df, length, indexAr, prevAr, numberOfParam, sublistsObj, variables, currentTestNumber)

                    if numberOfParam!=len(parameters)-1:
                        pickler('C:/Users/Billy/Documents/Code/ML_trends/Data/Patterns/recognisedPattern'+variable+str(currentTestNumber)+'.pickle',recognisedPatternAr)
                    else:
                        pickler('C:/Users/Billy/Documents/Code/ML_trends/Data/Patterns/recognisedPattern_AllVariables_TestNo.'+str(currentTestNumber)+'.pickle',recognisedPatternAr)
                    print(parameters)
##        save = False
##        prevLen = 0
##        while save == False:
##            listPatterns = dePickler('C:/Users/Billy/Documents/Code/ML_trends/Data/Patterns/recognisedPattern_AllVariables_TestNo.'+str(currentTestNumber)+'.pickle')
##            prevLen = len(listPatterns)
##            if prevLen<

        for count, patt in enumerate(listPatterns):
            plot = Grapher(patt, 30, variables)
            plot.graph()

            
def findPatterns(n, variable, parameter, startIndex, maxStopIndex, listPatterns, df, length, indexAr, prevAr, numberOfParam, sublistsObj, variables, currentTestNumber):
    recognisedPatternAr = []
    for z in range(n):
        currentPatternAr = []                                           #[var_1, var_2, ...], var_1 = [currentPattern, futureOut], currentPattern a list
        if numberOfParam == 0:
            currentIndex = random.randint(startIndex, maxStopIndex)
        else:
            currentIndex = listPatterns[z][7]
        currentPatternAr.append(sublistsObj.currentListMaker(df[variable].values,length,startIndex,currentIndex))
        patterns = patternRecognition(prevAr, length, parameter, indexAr)
        recognisedPatterns = patterns.find(currentPatternAr)            #list of found similar patterns, [find_1, find_2, ...], find_i=[var_1, var_2, var_3, ...]
        recognisedIndexes = patterns.indexes()
        recognisedOutcomes = patterns.outcomes()
        
        if len(recognisedPatterns)>1000:
            outcomeAr = []
            for outcome in recognisedOutcomes:
                outcomeAr.append(outcome[0])
            aveOutcome = sum(outcomeAr)/len(outcomeAr)                  #we're only really interested in the closing price outcome (0th variable)
            
            if numberOfParam == 0:
                recognisedPatternAr.append([recognisedPatterns, aveOutcome, recognisedOutcomes, recognisedIndexes, currentPatternAr, length, startIndex, currentIndex,df['Close'].index.values[startIndex], df['Close'].index.values[currentIndex]])
            else:
                listPatterns = dePickler('C:/Users/Billy/Documents/Code/ML_trends/Data/Patterns/recognisedPattern'+variables[numberOfParam-1]+str(currentTestNumber)+'.pickle')
                newAveOutcome = []
                newRecognisedPatterns = []
                newRecognisedOutcomes = []
                newRecognisedIndexes = []
                newCurrentPatternAr = []
                newStartIndex = 0
                newCurrentIndex = 0
                newLength = 0
                newCurrent = 0
                newStart = 0
                
                for count, index in enumerate(recognisedIndexes):
                    if index in listPatterns[z][3]:
                        indexOfPattern = listPatterns[z][3].index(index)
                        
                        recognisedPatternFromPrevious = listPatterns[z][0][indexOfPattern]
                        recognisedPatternFromPrevious.append(recognisedPatterns[count][0])
                        newRecognisedPatterns.append(recognisedPatternFromPrevious)

                        recognisedOutcomeFromPrevious = listPatterns[z][2][indexOfPattern]
                        recognisedOutcomeFromPrevious.append(recognisedOutcomes[count][0])
                        newRecognisedOutcomes.append(recognisedOutcomeFromPrevious)

                        newRecognisedIndexes.append(index)
                        

                if len(newRecognisedPatterns)>200:
                    newAveOutcome = listPatterns[z][1]
                    recognisedCurrentArFromPrevious = listPatterns[z][4]
                    recognisedCurrentArFromPrevious.append(currentPatternAr[0])
                    newCurrentPatternAr = recognisedCurrentArFromPrevious

                    newStartIndex=(listPatterns[z][6])
                    newCurrentIndex=(listPatterns[z][7])
                    newLength=(listPatterns[z][5])
                    newStart=(listPatterns[z][8])
                    newCurrent=(listPatterns[z][9])
                    recognisedPatternAr.append([newRecognisedPatterns, newAveOutcome, newRecognisedOutcomes, newRecognisedIndexes, newCurrentPatternAr, newLength, newStartIndex, newCurrentIndex, newStart, newCurrent])

        print('Test number:,',z,'\tMatched Patterns:',len(recognisedPatternAr),'\tParam:', parameter)
        
    return recognisedPatternAr                              

def pickler(directory, data):
        pickle_out = open(directory,'wb')
        pickle.dump(data,pickle_out)
        pickle_out.close()

def bubbleSort(listAr):
    n = len(listAr)
    for i in range(n):
        for j in range(0,n-i-1):
            if abs(listAr[j][1])>abs(listAr[j+1][1]):
                listAr[j], listAr[j+1]= listAr[j+1],listAr[j]
    return listAr

def dePickler(directory):
    pickle_in = open(directory,'rb')
    return pickle.load(pickle_in)            

