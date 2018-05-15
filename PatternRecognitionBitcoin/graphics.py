import matplotlib.pyplot as plt
class Grapher(object):

    def __init__(self, pattern, length, varName):
        self.recognisedPatterns = pattern[0] #[patt1, patt2, ...]
        self.aveOutcomes = pattern[1] #[patt1, patt2]
        self.recognisedOutcomes = pattern[1]
        self.currentPatt = pattern[4]
        self.length = length
        self.varName = varName


    def graph(self):
        xp = []
        xp2 = []
        endPriceLine = []
        for z in range(self.length):
            xp.append(z)
        fig = plt.figure()
        axes = []
        for count in range(len(self.recognisedPatterns[0])):
            if count==0:
                axes.append(plt.subplot2grid( (len(self.recognisedPatterns[0])+1,1), (count,0) ,rowspan=2, colspan=1))
            else:
                axes.append(plt.subplot2grid( (len(self.recognisedPatterns[0])+1,1), (count+1,0) ,rowspan=1, colspan=1, sharex=axes[0]))
            axes[count].set_ylabel(self.varName[count], rotation=0)

        for count, patt in enumerate(self.recognisedPatterns):
            if count <100:
                for count2, ax in enumerate(axes):
                    axes[count2].plot(xp, patt[count2], color='black', linewidth=0.06)
                    axes[count2].plot(xp, self.currentPatt[count2][0], color = 'green', linewidth = 0.1)
##                if self.aveOutcomes[count]>patt[0][-1]:
##                    pcolor = '#24bc00'
##                else:
##                    pcolor= '#d40000'
##                    
##                axes[0].scatter(self.length+5, self.aveOutcomes[count][0], c=pcolor, alpha=0.4)
        plt.show()
