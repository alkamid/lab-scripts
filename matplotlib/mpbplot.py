from cycler import cycler
import numpy as np
import matplotlib.pyplot as plt
import h5py

ctlscript = 'tri-defect-'

def read_bands_from_output(filename):
    with open(filename, 'r') as f, open(filename + '-TE.dat', 'w') as g, open(filename + '-TM.dat', 'w') as h:
        for line in f:
            if line.startswith('tmfreq'):
                h.write(line)
            elif line.startswith('tefreq'):
                g.write(line)

def generate_filenames(k=1, band=1, pol='tm'):
    file_Ez = '{0}e.k{1:02d}.b{2:02d}.z.{3}.h5'.format(ctlscript, k, band, pol)
    file_Hx = '{0}h.k{1:02d}.b{2:02d}.x.{3}.h5'.format(ctlscript, k, band, pol)
    file_Hy = '{0}h.k{1:02d}.b{2:02d}.y.{3}.h5'.format(ctlscript, k, band, pol)
    return file_Ez, file_Hx, file_Hy
                
def plot_mode(file1, file2, file3, title='', plot_vectors=False):#{{{
    # borrowed from https://github.com/FilipDominec/mpb-plotting/blob/master/plot_dispersion_and_modes.py
    contourcount = 100

    eps = np.array(h5py.File('{0}epsilon.h5'.format(ctlscript), "r")['data-new'])
    Ez_data = np.array(h5py.File(file1, "r")['z.r-new'])
    #Hx_data = np.array(h5py.File(file2, "r")['x.r-new'])
    #Hy_data = np.array(h5py.File(file3, "r")['y.r-new'])

    ## Location of data points
    xpoints = np.linspace(0, 1, len(Ez_data[0]))
    ypoints = np.linspace(0, 1, len(Ez_data))

    ## Plot the scalar values, normalize the field amplitude scale
    lvlextent = max(np.abs(np.min(Ez_data)), np.abs(np.max(Ez_data)))
    contours = plt.contourf(xpoints, ypoints, Ez_data, cmap=plt.cm.RdBu, levels=np.linspace(-lvlextent, lvlextent, contourcount), label='')

    #plt.contour(xpoints, ypoints, Ez_data, levels=[0], label='', colors='#00ff00', lw=2, alpha=.5)

    ## Plot permittivity
    plt.contour(xpoints, ypoints, eps, colors='k',alpha=1, label='', lw=4, levels=[5])

    ## Plot the vector field
    if plot_vectors:
        xgrid, ygrid    = np.meshgrid(xpoints, ypoints)                 ## the vector locations
        plt.quiver(xgrid, ygrid, Hy_data, Hx_data, pivot='middle', headwidth=3, headlength=6, label='')
    if title: plt.title(title)

    plt.axes().set_aspect('equal')

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    plt.savefig(file1[:-3] + '.png', transparent=True)


def plot_bands(filename):

    band = np.loadtxt(filename, usecols=[1], unpack=True, delimiter=',', skiprows=1) 
    Kx_allbands = np.loadtxt(filename, usecols=[2], unpack=True, delimiter=',', skiprows=1)
    with open(filename) as f:
        colcount = len(f.readlines()[0].split(','))

    freqs_allbands = np.loadtxt(filename, usecols=range(6,colcount-1), unpack=True, delimiter=',', skiprows=1)


    fig = plt.figure()
    ax = fig.add_subplot(111)


    cm = plt.get_cmap('Dark2')
    ax.set_prop_cycle(cycler('color', [cm(i/colcount) for i in range(colcount)]))

    for i in range(len(freqs_allbands)):
        ax.plot(freqs_allbands[i], lw=2)

    ax.set_ylim(top=0.6)

    plt.show()

def plot_allmodes(k=1, numbands=5):
    
    for b in range(1,numbands+1):
        fnames = generate_filenames(k=k, band=b)
        plot_mode(*fnames)

#read_bands_from_output('tri-nodefect.out')


#plot_bands('tri-nodefect.out-TM.dat')
