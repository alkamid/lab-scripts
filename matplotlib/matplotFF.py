import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import scipy.interpolate
import viridis

class matplotFF():
    """A class for plotting far-field measurements of lasers. It requires
    the 'x z signal' format, but supports stitched measurements — the data
    can be simply added at the end of a file    
    """
    def __init__(self, fig, BaseFilename, title = '', xLen=0, zLen=0, stitch=True):
        self.BaseFilename = BaseFilename
        self.title = title
        self.fig = fig
        
        self.rawData = np.loadtxt(self.BaseFilename)
        self.zRaw = self.rawData[:,0]
        self.xRaw = self.rawData[:,1]
        self.sigRaw = self.rawData[:,2]
        
        # figure out the number of steps for Z and X
        stage_tolerance = 0.05  # stages don't always move to the same
                                # place, so numerical positions might differ slightly
        if xLen == 0 and zLen == 0:
            z_unique_vals = [self.zRaw[0]]
            x_unique_vals = [self.xRaw[0]]

            # count unique values of Z/X values in the data file
            # (allows for non-rectangular data, i.e. for stiching together
            # patches)
            for i in range(len(self.zRaw)):
                if sum(abs(z_unique_vals-self.zRaw[i]) > stage_tolerance) == len(z_unique_vals):
                    z_unique_vals.append(self.zRaw[i])
            for i in range(len(self.xRaw)):
                if sum(abs(x_unique_vals-self.xRaw[i]) > stage_tolerance) == len(x_unique_vals):
                    x_unique_vals.append(self.xRaw[i])
            
            self.xLen = len(x_unique_vals)
            self.zLen = len(z_unique_vals)
        else:
            self.xLen = xLen
            self.zLen = zLen

        # fill in zeros if we are plotting a stiched far field
        if stitch == True:
            self.x = np.ndarray((self.xLen,self.zLen))
            self.z = np.ndarray((self.xLen,self.zLen))
            self.signal = np.zeros((self.xLen,self.zLen))
            for iz, z in enumerate(sorted(z_unique_vals)):
                for ix, x in enumerate(sorted(x_unique_vals)):
                     self.x[ix][iz] = x
                     self.z[ix][iz] = z
                     for i in zip(self.xRaw, self.zRaw, self.sigRaw):
                         if (abs(i[0]-x) < stage_tolerance) and (abs(i[1]-z) < stage_tolerance):
                             self.signal[ix][iz] = i[2]
                             break

        else:
            self.x = self.xRaw.reshape((self.xLen,self.zLen))
            self.z = self.zRaw.reshape((self.xLen,self.zLen))
            self.signal = self.sigRaw.reshape((self.xLen,self.zLen))

        # normalise the signal to [0, 1]
        self.signal -= np.min(self.signal)
        self.signal /= np.max(self.signal)

    def trim(self, xmin=None, xmax=None, zmin=None, zmax=None):
        self.x = self.x[zmin:zmax,xmin:xmax]
        self.z = self.z[zmin:zmax,xmin:xmax]
        self.signal = self.signal[zmin:zmax,xmin:xmax]

        # normalise the signal to [0, 1]
        self.signal -= np.min(self.signal)
        self.signal /= np.max(self.signal)

        
    def plotLine(self):
        '''plots the cross section of far-field (averaged all points at a set z position)'''

        av = [np.mean(row) for row in self.signal]
        zLine = [z[0] for z in self.z]

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

        self.ax1 = self.fig.add_subplot(111, polar=True)

        self.ax1.plot(theta, intens, color=color, linewidth=2.0, label=label)
        #self.ax1.set_theta_offset(-np.pi/2)
        self.ax1.get_yaxis().set_visible(False)
        
    def plot(self, rotate=False):
 

        self.ax1 = self.fig.add_subplot(111)
        self.ax1.margins(x=0)
        self.ax1.set_xlim(self.x.min(), self.x.max())
        
        viri = viridis.get_viridis()
        plt.pcolormesh(self.x,self.z,self.signal, cmap=viri, edgecolors='face')

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)
        self.ax1.tick_params(labelright=True, labeltop=True)
        
        return self.fig

    def plotInterpolate(self, xPoints, zPoints, rotate=False, origin='lower'):

        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel("X / mm")
        self.ax1.set_ylabel("Z / mm")

        xi, zi = np.linspace(self.x.min(), self.x.max(), xPoints), np.linspace(self.z.min(), self.z.max(), zPoints)
        xi, zi = np.meshgrid(xi, zi)

        rbf = scipy.interpolate.Rbf(self.x, self.z, self.signal, function='linear')
        sigi = rbf(xi, zi)

        # normalise again after interpolation — just so the colorbar
        # extends from 0 to 1
        sigi /= np.max(sigi)
        
        if rotate:
            sigi = np.rot90(sigi)

        viri = viridis.get_viridis()

        plt.imshow(sigi, extent=[self.x.min(), self.x.max(), self.z.min(), self.z.max()], origin=origin, cmap=viri, aspect='auto')

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)
        self.ax1.tick_params(labelright=True, labeltop=True)

    def show(self):
        plt.savefig(self.BaseFilename + '.pdf')
        plt.savefig(self.BaseFilename + '.png')
        plt.show()
