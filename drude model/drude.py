import math
import pylab

'''
This script calculates a few optical properties, namely:
- plasmon frequency
- complex relative permittivity
- AC and DC conductivities
It is useful for the mode analysis of a QCL (and, I imagine, any other semiconductor device), where these values are required to calculate the reflectivity of layers.

The Drude model should can be found in many books, but to write this code I used Mark Fox "Optical Properties of Solids", Second Edition, 2010, ISBN 978-0-19-957337-0, Chapter 7

With plasmaVsDopingPlot() you can plot plasma frequency and DC conductivity vs. the doping of GaAs (actually of any material, as long as ou provide the parameters in Material class). I used it to determine the highest possible doping for which a certain frequency lies above the plasma frequency, i.e. I wanted a layer that isn't reflective but is still DC conductive. The function doesn't require matplotlib module - you can simply export the data into a file if you don't have this module and plot with your preferred software.

ak763@cam.ac.uk 

'''

#constants:
e = 1.6e-19 # elementary charge in Coulombs
eps_0 = 8.85e-12 # vacuum permittivity in farads/meter
e_mass = 9.1e-31 # electron mass in kg

class Material:
    def __init__(self, name=None, mass=None, eps=None, tau=None):
        if name == None:
            name = 'GaAs'

        if name == 'GaAs':
            self.name = 'GaAs'

            if mass == None:
                self.mass = 0.067
            else:
                self.mass = mass

            if eps == None:
                self.eps = 13.3
            else:
                self.eps = eps

            if tau == None:
                self.tau = 1e-13
            else:
                self.tau = tau
        else:
            raise MaterialNotInDatabase("Material not found in the database. You can enter a custom material by calling Material(name,eff_mass, epsilon)")
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
        print "WARNING: The doping is very high (%s m^-3 = %s cm^-3). Are you sure you entered it in cm^-3?" % (round(doping), round(doping/1e6)) 
    omega = ((float(doping)*e**2)/(material.getEps()*eps_0*e_mass*material.getMass()))**(0.5)

    return omega


def epsilon(doping, material=Material('GaAs'), frequency=None):

    # calculate the real and imaginary part of the relative permittivity

    if frequency == None:
        print "Frequency not specified, using 2.9THz as default"
        frequency = 2.9e12
        
    omega = 2*math.pi*frequency
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
        print "Frequency not specified, using 2.9THz as default"
        frequency = 2.9e12

    im_eps = epsilon(doping, material, frequency)['imag']
    sigma = im_eps*eps_0*2*math.pi*frequency
    return sigma

def QCLPropertiesTable(freq = 2.9e12, AR = None, Plasmon1 = None, Plasmon2 = None):
    regions = locals()
    propertyList = []
    headings = ['doping (cm^-3)', 'Re(eps)', 'Im(eps)', 'sigma', 'f [THz]']
    i = 0
    for region in regions:
        if region != 'freq' and regions[region]:
            propertyList.append([])
            propertyList[i].append(region)
            propertyList[i].append(regions[region])
            eps = epsilon(regions[region], frequency=freq)
            propertyList[i].extend(['%.2f' % eps['real'], '%.2f' % eps['imag']])
            #propertyList[i].append('%.2f' % conductivity(regions[region]))
            propertyList[i].append('%.2f' % AC_conductivity(regions[region], frequency = 2.9e12))
            propertyList[i].append('%.2f' % (plasmaFrequency(regions[region])/(2*math.pi*1e12)) )
            i += 1
    row_format ="{:>15}" * (len(headings) + 1)
    print row_format.format("", *headings)
    for row in propertyList:
        print row_format.format(*row)

def PlasmaVsDopingPlot(dopingStart = 1e16, dopingStop = 1e18):
    data = [[], [], []]

    numPoints = 1000
    deltaDoping = (dopingStop-dopingStart)/numPoints

    outputText = ''
    
    for i in range(numPoints):
        currentDoping = dopingStart + i*deltaDoping
        plasma = plasmaFrequency(currentDoping)/(2*math.pi)
        sigma = AC_conductivity(currentDoping, frequency = 2.9e12)
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
    freq = ax1.plot(data[0], data[1], 'r')
    pylab.ylabel("Plasma frequency / THz")
    ax2 = fig.add_subplot(111, sharex=ax1, frameon=False)
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    pylab.ylabel("Conductivity / S/m")
    cond = ax2.plot(data[0], data[2], 'b')
    
    pylab.show()


QCLPropertiesTable(freq = 2.7e12, AR = 2.6e15, Plasmon1 = 1e18, Plasmon2 = 5e18)
PlasmaVsDopingPlot()
