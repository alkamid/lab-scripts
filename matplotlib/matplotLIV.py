import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

class matplotLIV():

    def __init__(self, BaseFilename, temperatures, length=None, width=None, area=None, title = '', ylim=None):
        self.BaseFilename = BaseFilename
        self.temperatures = temperatures
        if length and width:
            self.length = length
            self.width = width
            self.area = length*width*1e-5
        else:
            self.area = area
        self.title = title
        self.ylim = ylim
        
        filenames = [("%s_%sK.txt" % (self.BaseFilename, str(temp)), temp) for temp in self.temperatures]
        self.rawData = [(np.loadtxt(fname), temp) for fname, temp in filenames]
        self.colors = colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#e6ab02', '#a6761d', '#666666']

        self.maxValueRow = (0,0,0)

    def plot(self):
        
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        ax1 = self.ax1
        ax1.tick_params(bottom='off')
        ax1.xaxis.tick_top()
        self.ax2 = ax1.twinx()
        ax2 = self.ax2
        self.ax3 = ax2.twiny()
        ax3 = self.ax3
        ax3.xaxis.tick_bottom()

        ax1.set_xlabel("current / A")
        ax1.xaxis.set_label_position('top')
        ax1.set_ylabel("voltage / V")
        ax2.set_ylabel("light intensity / arb. u.")
        ax3.set_xlabel(r'current density / $\mathregular{Acm^{-2}}$')
        ax3.xaxis.set_label_position('bottom')

        for i, (datafile, label) in enumerate(self.rawData):
            self.checkMaxValues(datafile)
            ax1.plot( datafile[:,0], datafile[:,1], color=self.colors[i], label='%sK' % str(label))
            ax2.plot( datafile[:,0], datafile[:,2], color=self.colors[i], label='%sK' % str(label), linewidth=2)


        ax1.margins(x=0)

        ax1.grid(True, axis='y')
        ax3.grid(True)

        start, end = ax1.get_xlim()

        self.setAxesScale(ax1, ax2)
        if self.ylim:
            ax2.set_ylim(top=self.ylim)

        ax3.set_xlim(start/self.area, end/self.area)
        ax2.legend(loc='upper left')

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)

        loc = plticker.MultipleLocator(base=20.0) # this locator puts ticks at regular intervals
        ax3.xaxis.set_major_locator(loc)

    def checkMaxValues(self, data):
        maxInd = data.argmax(axis=0)[2]
        if data[maxInd][2] > self.maxValueRow[2]:
            self.maxValueRow = data[maxInd]

    def setAxesScale(self, ax1, ax2):
        yrange = ax1.get_ylim()
        y1Fraction = self.maxValueRow[1]/yrange[1]
        y2Fraction = y1Fraction - 0.02
        ax2.set_ylim(top=self.maxValueRow[2]/y2Fraction)

    def show(self):
        plt.savefig(self.BaseFilename + '.pdf')        
        plt.show()
