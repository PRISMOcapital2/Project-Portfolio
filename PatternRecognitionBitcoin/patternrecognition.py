import time

class patternRecognition(object):

    def __init__(self, prevAr, length, parameters, indexAr):
        self.prevAr = prevAr
        self.length = length
        self.firstVarArray = prevAr[0]
        self.similarPatterns = []
        self.patternOutcomes = []
        self.parameter = parameters
        self.patternIndexes = []
        self.indexAr = indexAr
        
        
    def find(self, currentAr):
        counter = 0
        for count in range(len(self.firstVarArray[0])):
            similarityAr = []
            for countVar, eachVarArray in enumerate(self.prevAr):
                similaritySubAr = []
                patternAr = eachVarArray[0]
                outcomeAr = eachVarArray[1]
                eachPattern = patternAr[count]
               
                for z in range(self.length):
                    similaritySubAr.append(abs(eachPattern[z]-currentAr[countVar][0][z]))          
                similarityAve = sum(similaritySubAr)/len(similaritySubAr)
                similarityAr.append(similarityAve)
            if all([similarityAr[0]<self.parameter]):
                simPat = []                                                     
                simOut = []
                for eachArray in self.prevAr:
                    eachPattern = eachArray[0][count]
                    eachOutcome = eachArray[1][count]                    
                    simPat.append(eachPattern)
                    simOut.append(eachOutcome)
                self.similarPatterns.append(simPat)
                self.patternOutcomes.append(simOut)
                self.patternIndexes.append(self.indexAr[count])
        return self.similarPatterns
        

    def outcomes(self):
        return self.patternOutcomes
    def indexes(self):
        return self.patternIndexes
