import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

matplotlib.rcParams['axes.labelsize'] = 18
matplotlib.rcParams['xtick.labelsize'] = 14
matplotlib.rcParams['ytick.labelsize'] = 14
matplotlib.rcParams['legend.fontsize'] = 14


class matplotLIV():

    def __init__(self, BaseFilename, temperatures, fig=None, length=None,
                 width=None, area=None, title = None, ylim=None,
                 sensitivity=None, dutycycle=None, detector='golay-tydex'):

        self.BaseFilename = BaseFilename
        self.temperatures = temperatures
        self.fig = fig

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
        self.colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#e6ab02', '#a6761d', '#666666']

        self.maxValueRow = (0,0,0)

        # sensitivity of detectors - measured by Dave Jessop, given in
        # mv/uW
        
        if sensitivity:
            self.sens = sensitivity
            
            sens_table = {'golay-tydex': 9.37,
                          'golay-cathodeon': 16.65,
                          'pyro': 6.25}

            # (1/10000) - because the number on the computer scales with sensitivity
            # (1/sqrt(2)) - RMS
            # (100/dutycycle) - the given power is extrapolated at CW
            # (/0.45) - the factor from square wave modulation
            power_scaling = 1/10000*sensitivity*np.sqrt(2)/sens_table[detector]*(100/dutycycle)/0.45

            for datafile, temp in self.rawData:
                datafile[:, 2] *= power_scaling

    def magnify(self, factors):
        assert len(factors) == len(self.rawData)
        new_rawdata = []
        for i, f in enumerate(factors):
            new_array = self.rawData[i][0]
            new_array[:, 2] *= f
            new_rawdata.append((new_array, self.rawData[i][1]))
        self.rawData = new_rawdata
        
    def plot(self, first_iv_only=False):
        
        if self.fig is None:
            self.fig = plt.figure(constrained_layout=True)

        self.ax1 = self.fig.add_subplot(111)
        ax1 = self.ax1
        ax1.tick_params(bottom=False)
        ax1.xaxis.tick_top()
        self.ax2 = ax1.twinx()
        ax2 = self.ax2
        self.ax3 = ax2.twiny()
        ax3 = self.ax3
        ax3.xaxis.tick_bottom()

        ax1.set_xlabel("current / A")
        ax1.xaxis.set_label_position('top')
        ax1.set_ylabel("voltage / V")
        ax3.set_xlabel(r'current density / $\mathregular{Acm^{-2}}$')
        ax3.xaxis.set_label_position('bottom')
        
        try:
            self.sens is None
        except AttributeError:
            ax2.set_ylabel("light intensity / arb. u.")
        else:
            if np.max(np.hstack([a[:, 2] for a,t in self.rawData])) > 1000:
                prefix = r'm'
                for datafile, temp in self.rawData:
                    datafile[:, 2] *= 0.001
            else:
                prefix = r'\mu'
            ax2.set_ylabel(r'peak output power / $\mathregular{' + prefix + r' W}$')

        ax1.grid(True, axis='y', zorder=0)
        ax3.grid(True)
        ax3.set_zorder(0)
        ax1.set_zorder(1)
        ax2.set_zorder(1)
        ax1.patch.set_visible(False)
        ax2.patch.set_visible(False)

        lns = []
        for i, (datafile, label) in enumerate(self.rawData):
            self.checkMaxValues(datafile)
            if i > 0:
                if first_iv_only is True:
                    pass
                else:
                    ax1.plot( datafile[:,0], datafile[:, 1], label='%sK' % str(label), zorder=1)
            else:
                ax1.plot( datafile[:, 0], datafile[:, 1], label='%sK' % str(label), zorder=1)
            lns += ax2.plot( datafile[:, 0], datafile[:, 2], label='%sK' % str(label), linewidth=2, zorder=1)

        # Define which lines to put in the legend. If you want l1 too, then use lns = l1+l2
        
        labs = [l.get_label() for l in lns]

        ax1.margins(x=0)
        start, end = ax1.get_xlim()

        self.setAxesScale(ax1, ax2)
        if self.ylim:
            ax2.set_ylim(top=self.ylim)

        if self.area is not None:
            ax3.set_xlim(start/self.area, end/self.area)
        
        if self.title:
            self.fig.suptitle(self.title, y=0.98, weight='bold')
            self.fig.subplots_adjust(top=0.86)

        self.leg = ax2.legend(lns,labs,loc='upper left')

    def changeTicks(self, base) -> None:
        """
        If the ticks on the bottom X axis (current density) are too sparse/dense, you can set the distance manually.
        Args:
            base:

        Returns:

        """

        loc = plticker.MultipleLocator(base)  # this locator puts ticks at regular intervals
        self.ax3.xaxis.set_major_locator(loc)

    def checkMaxValues(self, data):
        maxInd = data.argmax(axis=0)[2]
        if data[maxInd][2] > self.maxValueRow[2]:
            self.maxValueRow = data[maxInd]

    def setAxesScale(self, ax1, ax2):
        yrange = ax1.get_ylim()
        y1_fraction = self.maxValueRow[1]/yrange[1]
        y2_fraction = y1_fraction - 0.02
        ax2.set_ylim(top=self.maxValueRow[2]/y2_fraction)

    def set_x_limits(self, left=None, right=None):
        if left:
            self.ax1.set_xlim(left=left)
            if self.area is not None:
                self.ax3.set_xlim(left=left/self.area)
        if right:
            self.ax1.set_xlim(right=right)
            if self.area is not None:
                self.ax3.set_xlim(right=right/self.area)

    def show(self):
        plt.savefig(self.BaseFilename + '.svg')
        plt.savefig(self.BaseFilename + '.png', dpi=150)
        plt.savefig(self.BaseFilename + '.pdf')
        plt.show()
