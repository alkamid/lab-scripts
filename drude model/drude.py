import numpy as np
import pylab
from decimal import Decimal

"""
This script calculates a few optical properties, namely:
- plasmon frequency
- complex relative permittivity
- AC and DC conductivities
It is useful for the mode analysis of a QCL (and, I imagine, any other semiconductor device), where these values are required to calculate the reflectivity of layers.

The Drude model should can be found in many books, but to write this code I used Mark Fox "Optical Properties of Solids", Second Edition, 2010, ISBN 978-0-19-957337-0, Chapter 7

With plasmaVsDopingPlot() you can plot plasma frequency and DC conductivity vs. the doping of GaAs (actually of any material, as long as ou provide the parameters in Material class). I used it to determine the highest possible doping for which a certain frequency lies above the plasma frequency, i.e. I wanted a layer that isn't reflective but is still DC conductive. The function doesn't require matplotlib module - you can simply export the data into a file if you don't have this module and plot with your preferred software.

ak763@cam.ac.uk 

"""

#constants:
e = 1.6e-19 # elementary charge in Coulombs
eps_0 = 8.85e-12 # vacuum permittivity in farads/meter
e_mass = 9.1e-31 # electron mass in kg
c = 3e8 # speed of light

class RealEpsPositive(Exception):
    pass

class Material:
    
    def __init__(self, name=None, mass=None, eps=None, tau=None):
        self.material_db = {}
        self.material_db['GaAs'] = {'mass': 0.067, 'eps': 12.96, 'tau': 0.1e-12}
        self.material_db['GaAs_AR'] = {'mass': 0.067, 'eps': 12.96, 'tau': 0.5e-12}
        self.material_db['Au'] = {'mass': 1, 'eps': 1, 'tau': 0.6e-13}


        if name == None:
            print('Material not specified, using GaAs as the default')
            name = 'GaAs'

        try: self.mass = self.material_db[name]['mass']
        except KeyError:
            if mass is None or eps is None or tau is None:
                raise MaterialNotInDatabase("Material not found in the database. You can enter a custom material by calling Material(name,eff_mass, epsilon)")
            else:
                self.mass = mass
                self.eps = eps
                self.tau = tau
        else:
            self.eps = self.material_db[name]['eps']
            self.tau = self.material_db[name]['tau']
            
    def getMass(self):
        return self.mass
    def getEps(self):
        return self.eps
    def getTau(self):
        return self.tau


def plasmaFrequency(doping, material=Material('GaAs')):

    # calculate the plasma frequency for a given doping

    doping = doping*1e6 # convert to m^-3
    
    if doping > 1e30:
        print("WARNING: The doping is very high (%s m^-3 = %s cm^-3). Are you sure you entered it in cm^-3?" % (round(doping), round(doping/1e6)))
    omega = ((float(doping)*e**2)/(material.getEps()*eps_0*e_mass*material.getMass()))**(0.5)

    return omega


def epsilon(doping, material=Material('GaAs'), frequency=None):

    # calculate the real and imaginary part of the relative permittivity

    if frequency == None:
        print("Frequency not specified, using 2.9THz as default")
        frequency = 2.9e12
        
    omega = 2*np.pi*frequency
    eReal = material.getEps()*(1-(plasmaFrequency(doping, material)**2 * material.getTau()**2)/(1+omega**2 * material.getTau()**2))
    eImag = (material.getEps()*plasmaFrequency(doping, material)**2 * material.getTau())/(omega*(1+omega**2 * material.getTau()**2))
    
    return {'real' : eReal, 'imag' : eImag}

def DC_conductivity(doping, material=Material('GaAs')):
    # calculate the DC conductivity (useful for determining the resistance of the doped layer)
    
    doping = doping*1e6 # conversion to m^-3
    
    sigma = doping*e**2* material.getTau()/(material.getMass()*e_mass)
    return sigma

def AC_conductivity(doping, material=Material('GaAs'), frequency=None):

    # calculate the AC conductivity (used in the simulation of the optical mode)

    if frequency == None:
        print("Frequency not specified, using 2.9THz as default")
        frequency = 2.9e12

    im_eps = epsilon(doping, material, frequency)['imag']
    sigma = im_eps*eps_0*2*np.pi*frequency
    return sigma

# absorption coefficient, take from Fox's 2007 print (1st edition), eq. (1.23) for kappa and (1.16) for alpha
def absorption(doping=None, e1 = None, e2 = None, freq = 2.9e12, material = Material('GaAs')):
    if not (e1 or e2):
        eps = epsilon(doping, material)
        e1 = eps['real']
        e2 = eps['imag']

    if e1 > 0:
        raise RealEpsPositive("The real part of the dielectric constant is positive, so kappa is complex")
    else:
        kappa = 1/np.sqrt(2)*np.sqrt(-e1+np.sqrt(e1**2+e2**2))

    alpha = 2*2*np.pi*freq*kappa/c
    return alpha

# p. 147 in Fox, eq (7.20)
def skinDepth(doping = None, e1 = None, e2 = None, freq = 2.9e12, material = Material('GaAs')):
    if not (e1 or e2):
        delta = 2/absorption(doping = doping, freq = freq, material = material)
    else:
        delta = 2/absorption(e1 = e1, e2 = e2, freq = freq)
    return delta


def QCLPropertiesTable(freq = 2.9e12, AR = None, Plasmon1 = None, Plasmon2 = None):
    regions = locals()
    propertyList = []
    headings = ['doping (cm^-3)', 'Re(eps)', 'Im(eps)', 'sigma', 'f [THz]']
    i = 0
    for region in regions:
        if region != 'freq' and regions[region]:
            propertyList.append([])
            propertyList[i].append(region)
            propertyList[i].append('{0:.2E}'.format(Decimal(regions[region])))
            eps = epsilon(regions[region], frequency=freq)
            propertyList[i].extend(['{0:.2f}'.format(eps['real']), '%.2f' % eps['imag']])
            #propertyList[i].append('%.2f' % DC_conductivity(regions[region]))
            propertyList[i].append('%.2f' % AC_conductivity(regions[region], frequency = 2.9e12))
            propertyList[i].append('%.2f' % (plasmaFrequency(regions[region])/(2*np.pi*1e12)) )
            i += 1
    row_format ="{:>15}" * (len(headings) + 1)
    print(row_format.format("", *headings))
    for row in propertyList:
        print(row_format.format(*row))

def PlasmaVsDopingPlot(dopingStart = 1e16, dopingStop = 3e17):
    data = [[], [], []]

    numPoints = 1000
    deltaDoping = (dopingStop-dopingStart)/numPoints

    outputText = ''
    
    for i in range(numPoints):
        currentDoping = dopingStart + i*deltaDoping
        plasma = plasmaFrequency(currentDoping)/(2*np.pi)
        sigma = DC_conductivity(currentDoping)
        data[0].append(currentDoping)
        outputText += '%f' % currentDoping
        data[1].append(plasma)
        outputText += '\t %f' % plasma
        data[2].append(sigma)
        outputText += '\t %f\n' % sigma

    outputFile = open('PlasmaVsDoping.dat', 'w')
    outputFile.write(outputText)
    outputFile.close()

    fig = pylab.figure()
    pylab.xlabel("doping / cm^-3")
    ax1 = fig.add_subplot(111)
    ax1.yaxis.tick_left()

    ax1.grid(True)
    
    freq = ax1.plot(data[0], data[1])
    pylab.ylabel("Plasma frequency / Hz")
    ax2 = fig.add_subplot(111, sharex=ax1, frameon=False)
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    pylab.ylabel("Conductivity / S/m")
    next(ax2 ._get_lines.prop_cycler)['color']
    cond = ax2.plot(data[0], data[2])

    pylab.tight_layout()
    pylab.savefig('plasma_and_conductivity.pdf')
    pylab.show()


#print skinDepth(1e18)

# 5.61e15 - Amanti
    
QCLPropertiesTable(freq = 2.9e12, AR = 2.9e15, Plasmon1 = 5e18, Plasmon2 = 5.9e22)
#PlasmaVsDopingPlot()
