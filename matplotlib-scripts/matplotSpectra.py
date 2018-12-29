import csv
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Qt5Agg')

mpl.rcParams['axes.labelsize'] = 18
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14
mpl.rcParams['legend.fontsize'] = 14
plt.rcParams['figure.constrained_layout.use'] = True


class matplotSpectra():

    def __init__(self, BaseFilename, currents, offsets, title='', inverse=None, pisa_format=False):
        self.BaseFilename = BaseFilename
        self.currents = currents
        self.offsets = offsets
        self.title = title
        self.inverse = inverse
        self.pisa_format = pisa_format

        if pisa_format:
            filenames = [(f'{self.BaseFilename}-{cur}mV.csv', cur) for cur in self.currents]
            if Path(filenames[0][0]).exists():
                pass
            else:
                filenames = [(f'{self.BaseFilename}-{cur}mV.txt', cur) for cur in self.currents]
            self.rawData = []
            for fname, cur in filenames:
                with open(fname) as f:
                    reader = csv.reader(f, delimiter=',')
                    tempdata = []
                    read = False
                    for line in reader:

                        if read:
                            if not line:
                                break
                            tempdata.append([float(a) for a in line])
                        elif line == ['XYDATA']:
                            read = True
                self.rawData.append((np.array(tempdata), cur))


        else:
            filenames = [("%s-%sV.dpt" % (self.BaseFilename, cur), cur) for cur in self.currents]

            try: self.rawData = [(np.loadtxt(fname, delimiter=","), cur) for fname, cur in filenames]
            except ValueError:
                self.rawData = [(np.loadtxt(fname, delimiter="\t"), cur) for fname, cur in filenames]
            except OSError:
                filenames = [("%s_%sV.dpt" % (self.BaseFilename, cur), cur) for cur in self.currents]
                try: self.rawData = [(np.loadtxt(fname, delimiter=","), cur) for fname, cur in filenames]
                except ValueError:
                    self.rawData = [(np.loadtxt(fname, delimiter="\t"), cur) for fname, cur in filenames]
     
        # self.colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#e6ab02', '#a6761d', '#666666', '#666666', '#666666', '#666666']

    def plot(self, fig=None, scale=1):
        
        if fig:
            self.fig = fig
        else:
            self.fig = plt.figure()

        self.ax1 = self.fig.add_subplot(111)
        ax1 = self.ax1
        ax1.tick_params(axis="x", top=False)
        ax1.tick_params(axis="y", labelleft=False, left=False)
        
        self.ax3 = ax1.twiny()
        ax3 = self.ax3

        ax1.set_xlabel("frequency / THz")
        ax1.set_ylabel("light intensity / arb. u.")
        ax3.set_xlabel(r"wavelength / $\mathrm{\mu m}$")
        '''
        for i, (datafile, label) in enumerate(self.rawData):
            if i>0:
                adjustedYData = datafile[:,1]-self.rawData[0][0][:,1]+sum(self.offsets[:i-1])
                ax1.plot( datafile[:,0]*3e-2, adjustedYData, color=self.colors[i-1], label='%s' % label)
        '''
        for i, (datafile, label) in enumerate(self.rawData):
            if self.inverse and len(self.inverse) >= i and self.inverse[i] == 1:
                adjustedYData = datafile[:,1]*(-1)*self.inverse[i]
            else:
                adjustedYData = datafile[:,1]
            adjustedYData *= scale
            adjustedYData = adjustedYData+sum(self.offsets[:i])

            ax1.plot( datafile[:,0]*3e-2, adjustedYData, lw=2, label='%s' % label)


        ax1.margins(x=0)

        ax1.grid(True, axis='x')

        start, end = ax1.get_xlim()
        factor = 3e8/1e12*1e6
        if abs(start) < 1:
            top_axis_start = 0
        else:
            top_axis_start = factor/start

        ax3.set_xlim(top_axis_start, factor/end)

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        # self.fig.subplots_adjust(top=0.86)

    def addLabels(self, xPosition, offset=0.25, current=False):
        ln = self.ax1.get_lines()
        for i, line in enumerate(ln):
            data = line.get_data()
            idx = (np.abs(data[0]-xPosition)).argmin()
            yVal = data[1][idx]
            text = self.rawData[i][1] + ('A' if current else 'V')
            self.ax1.text(xPosition, yVal-offset, text, color=line.get_color())

    def show(self):
        plt.savefig(self.BaseFilename + '.pdf')
        plt.savefig(self.BaseFilename + '.png', dpi=300, transparent=True)
        plt.show()
