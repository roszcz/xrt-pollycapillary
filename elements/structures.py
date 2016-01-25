import numpy as np
import matplotlib.pyplot as plt
from random import random as rand

class HexStructure(object):
    def __init__(self, capillary_diameter = 0.01,\
                rIn = 0.005,\
                wall= 0.005,\
                nx_capillary = 5,\
                ny_bundle = 3):
        """ Class encapsulating hexagonal structure of capillaries """
        # Outer diameter (touching)
        self.rIn = rIn
        self.wall= wall
        self.capillary_diameter = 2*(self.rIn+self.wall)

        # Number of bundles along vertical direction (must be odd)
        self.ny_bundle = ny_bundle

        # Number of capillaries in bundle along 
        # horizontal direction (must be odd)
        self.nx_capillary = nx_capillary

        # Check oddity
        if self.ny_bundle % 2 == 0:
            print "Number of bundles must be odd, adding one"
            self.ny_bundle += 1
        if self.nx_capillary %2 ==0:
            print "Number of capillaries must be odd, adding one"
            self.nx_capillary += 1

        # Inner diameter (x-ray microsource ? )
        self.channel_diameter = self.capillary_diameter * 0.5

        # Spacing between capilaries (touching)
        self.bundlespacing = (self.nx_capillary - 1) *\
                                self.capillary_diameter *\
                                np.sqrt(3)/2 + self.capillary_diameter

        self.capillary_lens_xy()

    def capillary_bundle_xy(self, xbundle, ybundle, sigma):
        """ Generate budle of capillaries """
        nxpol_capillary = (self.nx_capillary - 1)/2

        atemp = self.capillary_diameter * nxpol_capillary

        # Prepare returned lists
        xci = []
        yci = []
        for ix in range(-2*nxpol_capillary, 2*nxpol_capillary +1):
            for iy in range(-2*nxpol_capillary, 2*nxpol_capillary +1):

                x0 = self.capillary_diameter * ix +\
                    self.capillary_diameter/2.*iy + \
                    0.* sigma * (rand() - 0.5) * \
                    (self.capillary_diameter - self.channel_diameter)

                y0 = np.sqrt(3)/2 * self.capillary_diameter * iy +\
                    0.* sigma * (rand() - 0.5) * \
                    (self.capillary_diameter - self.channel_diameter)

                in_bundle = self.in_hexagon(x0, y0,\
                            self.capillary_diameter * nxpol_capillary)

                if in_bundle:
                    xci.append(xbundle + x0)
                    yci.append(ybundle + y0)

        return xci, yci

    def capillary_lens_xy(self, sigma_position = 0.1):
        """ Get coordinates of bundles within the lens """
        # This has to be an integer, do not add dots
        nypol_bundle = (self.ny_bundle - 1)/2

        # Prepare return containers
        xci = []
        yci = []
        xi = []
        yi = []

        # Add + 1 because range is 0 based...
        for ix in range(-2*nypol_bundle, 2*nypol_bundle +1):
            #print str(ix)
            for iy in range(-2*nypol_bundle, 2*nypol_bundle +1):

                x0 = np.sqrt(3)/2.0 * self.bundlespacing * iy +\
                        0 * sigma_position * (rand()-0.5) *\
                        (self.capillary_diameter - self.channel_diameter)

                y0 = ix * self.bundlespacing + \
                        iy * self.bundlespacing / 2.0 + \
                        0 * sigma_position * (rand()-0.5) *\
                        (self.capillary_diameter - self.channel_diameter)

                # NOTE - look out for order of arguments (x and y)
                in_lens = self.in_hexagon(y0, x0,\
                          self.bundlespacing * nypol_bundle)

                if in_lens:
                    #print x0, y0
                    xci0, yci0 = self.capillary_bundle_xy(x0, y0,\
                                    sigma_position)
                    # Appending single values simply extends the list
                    xi.append(x0)
                    yi.append(y0)
                    # Appending lists creates a list of lists, we want
                    # just a 1D vectors of capillaries' positions (?)
                    # Joining lists is simply adding them
                    xci = xci + xci0
                    yci = yci + yci0

        self.xi = xi
        self.yi = yi
        self.xci = xci
        self.yci = yci

    def in_hexagon(self, x, y, d):
        """ Check if (x, y) is in a hexagon defined by *d* """
        tol = 1.001

        war1 = abs(y) <= d * tol * np.sqrt(3)/2
        war2 = abs(np.sqrt(3)/2* x + 1/2. * y) <= tol * d * np.sqrt(3)/2
        war3 = abs(np.sqrt(3)/2* x - 1/2. * y) <= tol * d * np.sqrt(3)/2

        return war1 and war2 and war3

    def polar_coordinates(self):
        """ Generator to iterate over the whole structure
        >>> for r, phi in structure.polar_cooridnates():"""
        for x, y in zip(self.xci, self.yci):
            r = np.sqrt(x**2 + y**2)
            phi = np.arctan2(y,x)
            yield r, phi

    def capillary_radius(self):
        """ Entrance radius getter """
        return self.rIn

    def plot(self, save = False):
        """ Check the structure as separated from the capillaries """
        print 'Number of entrance channels:', len(self.xci)
        plt.plot(self.xci, self.yci,'ko')
        #plt.xlim(-.1,.1)
        #plt.ylim(-.1,.1)
        if save:
            plt.savefig('entrance_stucture_pointplot.png')
        plt.show()

if __name__ == '__main__':
    """ python elements/structures.py """
    hello = HexStructure(nx_capillary=5, ny_bundle=3)
    hello.plot()
