import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.interpolate
from PIL import Image
matplotlib.use('Qt5Agg')


class matplotFF():
    """A class for plotting far-field measurements of lasers. It requires
    the 'x z signal' format, but supports stitched measurements — the data
    can be simply added at the end of a file    
    """
    def __init__(self, fig, BaseFilename, title='', xLen=0, zLen=0, stitch=True, distance=None, angular_direction=None,
                 output_filename=None):
        self.BaseFilename = BaseFilename
        if output_filename is None:
            self.output_filename = BaseFilename
        else:
            self.output_filename = output_filename
        self.title = title
        self.fig = fig
        
        self.rawData = np.loadtxt(self.BaseFilename)
        self.zRaw = self.rawData[:,0]
        self.xRaw = self.rawData[:,1]
        self.sigRaw = self.rawData[:,2]

        self.xlim = (None, None)
        self.zlim = (None, None)
        z_pixdim = (self.zRaw.max() - self.zRaw.min()) / len(self.zRaw)
        x_pixdim = (self.xRaw.max() - self.xRaw.min()) / len(self.xRaw)
        self.pixdim = (x_pixdim, z_pixdim)

        self.distance = distance
        self.angular_direction = angular_direction
        if distance is not None:
            if angular_direction == 'x':
                self.xRaw = 180/(2*np.pi)*np.arctan(self.xRaw/distance)
            elif angular_direction == 'z':
                self.zRaw = 180/(2*np.pi)*np.arctan(self.zRaw/distance)

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

        # fill in zeros if we are plotting a stitched far field
        if stitch:
            self.x = np.ndarray((self.zLen,self.xLen))
            self.z = np.ndarray((self.zLen,self.xLen))
            self.signal = np.zeros((self.zLen, self.xLen))
            for iz, z in enumerate(sorted(z_unique_vals)):
                for ix, x in enumerate(sorted(x_unique_vals)):
                    self.x[iz][ix] = x
                    self.z[iz][ix] = z
                    for i in zip(self.xRaw, self.zRaw, self.sigRaw):
                        if (abs(i[0]-x) < stage_tolerance) and (abs(i[1]-z) < stage_tolerance):
                            self.signal[iz][ix] = i[2]
                            break

        else:
            self.x = self.xRaw.reshape((self.zLen,self.xLen))
            self.z = self.zRaw.reshape((self.zLen,self.xLen))
            self.signal = self.sigRaw.reshape((self.zLen,self.xLen))

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
            angleData: if True, it means that the data were collected with a rotation stage and therefore do not have to be converted into angle
        """

        if mean:
            intens = np.mean(self.signal, axis=0)
        else:
            intens = self.signal[-5]
            intens = np.mean(self.signal)

        if angleData:
            theta = self.x[0]*np.pi/180
        else:
            theta = [np.arctan(z[0]/distance)+phaseShift for z in self.z]
            
        # normalize values to [0,1]
        intens -= np.min(intens)
        intens /= np.max(intens)

        self.ax1 = self.fig.add_subplot(111, polar=True)

        self.ax1.plot(theta, intens, color=color, linewidth=2.0, label=label)
        #self.ax1.set_theta_offset(-np.pi/2)
        self.ax1.get_yaxis().set_visible(False)
        
    def plot(self, rotate=False):
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.margins(x=0)
        self.ax1.set_xlim(self.x.min(), self.x.max())

        plt.pcolormesh(self.x,self.z,self.signal, edgecolors='face')

        self.fig.suptitle(self.title, y=0.98, weight='bold')
        self.fig.subplots_adjust(top=0.86)
        self.ax1.tick_params(labelright=True, labeltop=True)
        
        return self.fig

    def crosssection_plot(self, axis=0, subplot=None):
        cs = np.mean(self.signal, axis=axis)
        cs /= np.max(cs)

        self.ax_cutline[axis] = self.fig.add_subplot(subplot)
        ax = self.ax_cutline[axis]

        xlim = self.ax1.get_xlim()
        ylim = self.ax1.get_ylim()
        ratio = abs(xlim[1]-xlim[0])/abs(ylim[1]-ylim[0])

        if axis == 0:
            ax.plot(self.x[0, :], cs)
            ax.set_aspect(ratio*7)
            ax.set_xlim(xlim)
            ax.set_ylim([0, 1.05])
            ax.xaxis.set_label_position('top')
            ax.xaxis.set_ticks_position('top')

            ax.set_xlabel(r"$\theta$ / degrees")
            ax.set_ylabel("intensity / arb. u.", fontsize=7)
            self.ax1.xaxis.label.set_visible(False)
        elif axis == 1:
            ax.plot(cs, self.z[:, 0])
            ax.set_xlim([1.05, 0])
            ax.set_ylim(ylim)
            ax.set_aspect(ratio/7)
            if self.distance is not None and self.angular_direction == 'z':
                ax.set_ylabel("$\phi$ / degrees")
            else:
                ax.set_ylabel("Z / mm")

            ax.set_xlabel("intensity / arb. u.", fontsize=7)

            self.ax1.yaxis.label.set_visible(False)
        #self.gs1.update(wspace=0.025, hspace=0.05) # set the spacing between axes. 

    def plotInterpolate(self, xPoints, zPoints, rotate=False, origin='lower', cutlines=False):
        if not cutlines:
            self.ax1 = self.fig.add_subplot(111)
        else:
            #self.gs1 = gridspec.GridSpec(2, 2)
            #self.gs1.update(wspace=0.025, hspace=0.05) # set the spacing between axes. 

            self.ax1 = self.fig.add_subplot(224)
            self.ax_cutline = [None, None]

            self.ax1.tick_params(labelright=True, labelbottom=True, labelleft=False, bottom=True, right=True, left=False)

        self.ax1.set_xlabel(r"$\theta$ / degrees")
        if self.distance is not None and self.angular_direction == 'z':
            self.ax1.set_ylabel("$\phi$ / degrees")
        else:
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

        sigi[-1, -1] = 0

        pltmesh = plt.imshow(sigi, extent=[self.x.min(), self.x.max(), self.z.min(), self.z.max()], origin=origin,
                             aspect='auto')
        self.ax1.set_facecolor(pltmesh.cmap(0.0))
        cb = self.fig.colorbar(pltmesh, ticks=[0, 1])
        cb.set_label('light intensity / arb. u.')

        if cutlines:
            self.crosssection_plot(axis=0, subplot=222)
            self.crosssection_plot(axis=1, subplot=223)
            self.fig.subplots_adjust(hspace=-0.1, wspace=-0.2)
        #self.fig.suptitle(self.title, y=0.98, weight='bold')
        #self.fig.subplots_adjust(top=0.12, left=0.7)

        #self.ax1.tick_params(labelright=True, labeltop=True)

    def insert_laser_orientation(self, orientation_image_path, x, y):
        # https://stackoverflow.com/questions/3609585/how-to-insert-a-small-image-on-the-corner-of-a-plot-with-matplotlib
        im = Image.open(orientation_image_path)
        height = im.size[1]

        im = np.array(im).astype(np.float) / 255
        self.fig.figimage(im, x, self.fig.bbox.ymax - height - y)

    def show(self):
        plt.savefig(self.output_filename + '.pdf')
        plt.savefig(self.output_filename + '.svg')
        plt.savefig(self.output_filename + '.png', transparent=True)
        plt.show()
