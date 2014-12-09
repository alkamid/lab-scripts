import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import scipy.interpolate

class matplotFF():

    def __init__(self, BaseFilename, title = '', xLen=0, yLen=0):
        self.BaseFilename = BaseFilename
        self.title = title
        
        self.rawData = np.loadtxt(self.BaseFilename)
        self.xRaw = self.rawData[:,0]
        self.yRaw = self.rawData[:,1]
        self.zRaw = self.rawData[:,2]
        if xLen == 0 and yLen == 0:
            self.xLen = np.sqrt(len(self.xRaw))
            self.yLen = self.xLen

        self.x = self.xRaw.reshape((self.xLen,self.yLen))
        self.y = self.yRaw.reshape((self.xLen,self.yLen))
        self.z = self.zRaw.reshape((self.xLen,self.yLen))

    def plot(self):
        
 
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.margins(x=0)
        ax1.set_xlim(self.x.min(), self.x.max())
        
        plt.pcolormesh(self.x,self.y,self.z, cmap='rainbow')
        plt.show()

    def plotInterpolate(self, xPoints, yPoints):

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel("X / mm")
        ax1.set_ylabel("Y / mm")

        xi, yi = np.linspace(self.x.min(), self.x.max(), xPoints), np.linspace(self.y.min(), self.y.max(), yPoints)
        xi, yi = np.meshgrid(xi, yi)

        rbf = scipy.interpolate.Rbf(self.x, self.y, self.z, function='linear')
        zi = rbf(xi, yi)

        plt.imshow(zi, extent=[self.x.min(), self.x.max(), self.y.min(), self.y.max()], cmap='rainbow')
        plt.show()
