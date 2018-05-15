import os
import pickle
import datetime

class SubLists(object):

    def __init__(self, data, length, tick, exchange, newData, variables):
        self.data = data
        self.variable = variables
        self.length = length
        self.ticker = tick
        self.directory = 'C:/Users/Billy/Documents/Code/ML_trends/'
        self.exchange = exchange
        self.newData = newData
        self.filename = ''
        for var in variables:
            self.filename = self.filename+var
        self.indexAr = []
        
    def returnLists(self, start, stop):
        directory = (self.directory+'Data/Percentage_Data/'+self.exchange+'_'+self.tickDir(self.ticker)+'.pickle')
        if os.path.isfile(self.directory+'Data/Percentage_Data/'+self.exchange+'_'+self.tickDir(self.ticker)+'.pickle') and self.newData==False:
            sublistArray =(self.dePickler(self.directory+'Data/Percentage_Data/'+self.exchange+'_'+self.tickDir(self.ticker)+'.pickle'))      
            return sublistArray
        elif self.newData==True or not os.path.isfile(self.directory+'Data/Percentage_Data/'+self.exchange+'_'+self.tickDir(self.ticker)+'.pickle'):
            
            sublistArray = []
            sublistArray.append(self.prevListMaker(self.data[self.variable].values, start, stop))
            
            self.pickler(self.directory+'Data/Percentage_Data/'+self.exchange+'_'+self.tickDir(self.ticker)+'.pickle',sublistArray)
            return sublistArray
        

    def prevListMaker(self, data, start, stop):
        patternAr = []
        outcomeAr = []
        while start < stop:
            newPattern = []
            for z in range(self.length)[::-1]:
                newPattern.append(self.percentChangeFunc(data[start-self.length],data[start-z]))
            outcomeRange = data[start+20:start+30]
            currentPoint = data[start]
            avgOutcome = sum(outcomeRange)/len(outcomeRange)
            futureOutcome = self.percentChangeFunc(currentPoint, avgOutcome)
            outcomeAr.append(futureOutcome)
            patternAr.append(newPattern)            
            start+=1
            self.indexAr.append(start)
            
        return [patternAr, outcomeAr]

    def currentListMaker(self, data, length, startIndex, stopIndex):
        currentPattern = []
        for z in range(length+1)[:0:-1]:
            currentPattern.append(self.percentChangeFunc(data[stopIndex-(length+1)],data[stopIndex-z]))
        outcomeRange = data[stopIndex+20:stopIndex+30]
        currentPoint = data[stopIndex]
        avgOut = sum(outcomeRange)/len(outcomeRange)
        futureOut = self.percentChangeFunc(currentPoint, avgOut)

        return [currentPattern, futureOut]
            
    def percentChangeFunc(self, current, previous):
        if current==0 or previous==0:
            return 0
        try:
            x = float(current-previous)/abs(previous)*100
            return x
        except:
            return 0.0000000000000000001

    def pickler(self, directory, data):
        pickle_out = open(directory,'wb')
        pickle.dump(data,pickle_out)
        pickle_out.close()
    
    def dePickler(self, directory):
        pickle_in = open(directory,'rb')
        return pickle.load(pickle_in)

    def tickDir(self, ticker):
        #makes the ticker a save-able format
        if '/' in ticker:
            dex = ticker.find('/')
            return ticker[:dex]+'_'+ticker[dex+1:]
        else:
            return ticker


