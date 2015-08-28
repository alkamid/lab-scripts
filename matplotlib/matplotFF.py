import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import scipy.interpolate
import viridis

class matplotFF():

    def __init__(self, fig, BaseFilename, title = '', xLen=0, zLen=0):
        self.BaseFilename = BaseFilename
        self.title = title
        self.fig = fig
        
        self.rawData = np.loadtxt(self.BaseFilename)
        self.zRaw = self.rawData[:,0]
        self.xRaw = self.rawData[:,1]
        self.sigRaw = self.rawData[:,2]
        
        # figure out the number of steps for Z and X
        if xLen == 0 and zLen == 0:
            firstValue = self.zRaw[0]
            for i in range(len(self.zRaw)):
                if self.zRaw[i] > firstValue:
                    self.zLen = i
                    break
            self.xLen = len(self.zRaw)/self.zLen
        else:
            self.xLen = xLen
            self.zLen = zLen
        
        self.x = self.xRaw.reshape((self.xLen,self.zLen))
        self.z = self.zRaw.reshape((self.xLen,self.zLen))
        self.signal = self.sigRaw.reshape((self.xLen,self.zLen))

    def plotLine(self):
        '''plots the cross section of far-field (averaged all points at a set z position)'''

        av = [np.mean(row) for row in self.signal]
        zLine = [z[0] for z in self.z]

        #self.fig = plt.figure()

        plt.plot(av, zLine, color='#1b9e77')

    def plotLineAngle(self, distance=0, phaseShift=0, mean=True, angleData=False, color='#1b9e77', label=''):
        """plots the cross section of far-field (averaged all points at a set z position)

        Args:
            distance: distance of the detector in mm (for conversion into theta)
            phaseShift: angle in radians. Sometimes we want to shift the farfield by pi to get the plot on the other side of the polar coordinate system
        """

        if mean:
            intens = [np.mean(row) for row in self.signal]
        else:
            intens = self.signal[-5]
            intens = np.mean(self.signal,axis=0)
        
            
        if angleData:
            theta = self.x[0]*np.pi/180
        else:
            theta = [np.arctan(z[0]/distance)+phaseShift for z in self.z]
            
        # normalize values to [0,1]
        intens-= np.min(intens)
        intens/= np.max(intens)

        #self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111, polar=True)

        self.ax1.plot(theta, intens, color=color, linewidth=2.0, label=label)
        #self.ax1.set_theta_offset(-np.pi/2)
        self.ax1.get_yaxis().set_visible(False)
        
    def plot(self):
 
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.margins(x=0)
        self.ax1.set_xlim(self.x.min(), self.x.max())
        
        viri = viridis.get_viridis()
        plt.pcolormesh(self.x,self.z,self.signal, cmap=viri)

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)
        self.ax1.tick_params(labelright=True, labeltop=True)
        
        return self.fig

    def plotInterpolate(self, xPoints, zPoints, rotate=False, origin='lower'):

        #self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel("X / mm")
        self.ax1.set_ylabel("Z / mm")

        xi, zi = np.linspace(self.x.min(), self.x.max(), xPoints), np.linspace(self.z.min(), self.z.max(), zPoints)
        xi, zi = np.meshgrid(xi, zi)

        rbf = scipy.interpolate.Rbf(self.x, self.z, self.signal, function='linear')
        sigi = rbf(xi, zi)
        if rotate:
            sigi = np.rot90(sigi)
        plt.imshow(sigi, extent=[self.x.min(), self.x.max(), self.z.min(), self.z.max()], origin=origin, cmap='coolwarm', aspect='auto')

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)
        self.ax1.tick_params(labelright=True, labeltop=True)

        #return self.fig

    def show(self):
        plt.savefig(self.BaseFilename + '.pdf')
        plt.show()
