import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.rcParams['axes.labelsize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 14


class ModePlot:
    def __init__(self, fname_1d, fname_2d, fig=None, um=True):
        self.fname_1d = fname_1d
        self.fname_2d = fname_2d
        self.data_1d = np.loadtxt(self.fname_1d, skiprows=8, delimiter=',')
        self.img2d = mpimg.imread(self.fname_2d)
        self.fig = fig
        if um is True:
            self.data_1d[:, 0] *= 1e6
        self.zero = 0
        self.ax1d = None
        self.ax2d = None

    def set_zero(self, y):
        self.zero = y

    def set_1d_limits(self, low, up):
        self.ax1d.set_ylim([up, low])
        img_aspect = self.ax2d.get_data_ratio()
        self.ax1d.set_aspect(img_aspect/(up-low)*1.1)
        self.fig.subplots_adjust(wspace=0.05)

    def prepare_plot(self):
        self.ax2d = self.fig.add_subplot(121)
        self.ax2d.imshow(self.img2d)
        self.ax2d.axis('off')
        xlim = self.ax2d.get_xlim()
        middle = (xlim[1] - xlim[0]) / 2
        self.ax2d.axvline(middle, linestyle='--', color='C1')

        self.ax1d = self.fig.add_subplot(122)
        self.ax1d.plot(self.data_1d[:, 1]/np.max(self.data_1d[:, 1]), self.zero-self.data_1d[:, 0])

        self.ax1d.set_ylabel(r'distance / $\mathrm{\mu m}$')
        self.ax1d.set_xlabel(r'$\vert E \vert$ / arb. u.')
        self.ax1d.yaxis.set_label_position('right')

        self.ax1d.set_xticks([0, 1])

        self.ax1d.yaxis.tick_right()
        self.fig.tight_layout()
        
    def show(self):
        plt.show()

    def save(self, filename=None):
        if filename is None:
            filename = self.fname_2d[:-4] + '.pdf'
        plt.savefig(filename, bbox_inches='tight')
