# -*- coding: utf-8 -*-

import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

class matplotSpectra():

    def __init__(self, BaseFilename, currents, offsets, title=''):
        self.BaseFilename = BaseFilename
        self.currents = currents
        self.offsets = offsets
        self.title = title

        filenames = [("%s-%sV.dpt" % (self.BaseFilename, cur), cur) for cur in self.currents]
        self.rawData = [(np.loadtxt(fname, delimiter=","), cur) for fname, cur in filenames]
        self.colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#e6ab02', '#a6761d', '#666666', '#666666', '#666666', '#666666']


    def plot(self):
        
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        ax1 = self.ax1
        ax1.tick_params(axis="x", top="off")
        
        self.ax3 = ax1.twiny()
        ax3 = self.ax3

        ax1.set_xlabel("frequency / THz")
        ax1.set_ylabel("intensity / arb. u.")
        ax3.set_xlabel(r"wavelength / $\mathrm{\mu m}$")

        for i, (datafile, label) in enumerate(self.rawData):
            if i>0:
                adjustedYData = datafile[:,1]-self.rawData[0][0][:,1]+sum(self.offsets[:i-1])
                ax1.plot( datafile[:,0]*3e-2, adjustedYData, color=self.colors[i-1], label='%s' % label)

        ax1.margins(x=0)

        ax1.grid(True, axis='x')

        start, end = ax1.get_xlim()
        factor = 3e8/1e12*1e6
        ax3.set_xlim(factor/start, factor/end)

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)

    def addLabels(self, xPosition):
        ln = self.ax1.get_lines()
        for i, line in enumerate(ln):
            data = line.get_data()
            idx = (np.abs(data[0]-xPosition)).argmin()
            yVal = data[1][idx]
            self.ax1.text(xPosition, yVal-0.65, '%sV' % self.rawData[i+1][1], color=line.get_color())

    def show(self):
        plt.savefig(self.BaseFilename + '.pdf')
        plt.show()
