import numpy as np
import bendshapes as bs
import matplotlib.pyplot as plt
from elements import structures as st
import xrt.backends.raycing as raycing
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.materials as rm

class Capillary(roe.OE):
    """ Single light transmitting pipe """
    def __init__(self, *args, **kwargs):
        """ Abstract init """
        # Get y-dimension limits - by default capillary 
        # stretches from 10 to 100 mm
        self.y_entrance = kwargs.pop('y_entrance', 10)
        self.y_outrance = kwargs.pop('y_outrance', 100)

        # Update kwargs to fit xrt.OpticalElement constructor
        kwargs.update({'limPhysY' : (self.y_entrance, self.y_outrance)})

        # Get other entrance cooridinatesn
        self.x_entrance = kwargs.pop('x_entrance', 0)
        self.z_entrance = kwargs.pop('z_entrance', 0)
        # x and z outrance are defined by the capillary shape
        # and should not be of any concern here

        # We also need entrance coordinates
        # in the polar perspective
        # FIXME some seriuos foobar ove rhere
        self.phi_entrance =\
        np.arctan2(self.x_entrance, self.z_entrance) - np.pi/2
        self.r_entrance = np.sqrt(self.x_entrance**2 + self.z_entrance**2)

        # In xrt phi_entrance is equal to the roll
        kwargs.update({'roll' : self.phi_entrance})

        # Capital letter R will be denoting capillary 
        # radius rather then polar coordinate
        self.R_in = kwargs.pop('R_in', 1)

        # Init parent class 
        roe.OE.__init__(self, *args, **kwargs)
        self.isParametric = True

    def local_x0(self, s):
        """ Center of the capillary """
        return self.p[0] + self.p[1]*s + self.p[2]*s**2\
                + self.p[3]*s**3 + self.p[4]*s**4 + self.p[5]*s**5

    def local_x0Prime(self, s):
        """ Derivative of x0 """
        return self.p[1] + 2*self.p[2]*s + 3*self.p[3]*s**2\
                + 4*self.p[4]*s**3 + 5*self.p[5]*s**4

    def local_r0(self, s):
        """ Radius of the capillary (wall - x0 distance) """
        return self.pr[0] + self.pr[1]*s + self.pr[2]*s**2

    def local_r0Prime(self,s):
        """ Derivative of radius """
        return self.pr[1] + 2*self.pr[2]*s

    def local_r(self, s, phi):
        """ ? """
        # FIXME - i still am not sure what is all of this doing
        den = np.cos(np.arctan(self.local_x0Prime(s)))**2
        return self.local_r0(s) / (np.cos(phi)**2/den + np.sin(phi)**2)

    def local_n(self, s, phi):
        """ normal to the surface """
        a = -np.sin(phi)
        b = -np.sin(phi)*self.local_x0Prime(s) - self.local_r0Prime(s)
        c = -np.cos(phi)
        norm = np.sqrt(a**2 + b**2 + c**2)
        return a/norm, -b/norm, c/norm

    def xyz_to_param(self, x, y, z):
        """ *s*, *r*, *phi* are cylindrc-like coordinates of the capillary.
        *s* is along y in inverse direction, started at the exit,
        *r* is measured from the capillary axis x0(s)
        *phi* is the polar angle measured from the z (vertical) direction."""
        s = y
        phi = np.arctan2(x - self.local_x0(s), z)
        r = np.sqrt((x-self.local_x0(s))**2 + z**2)
        return s, phi, r

    def param_to_xyz(self, s, phi, r):
        """ coordinate transformation """
        x = self.local_x0(s) + r*np.sin(phi)
        y = s
        z = r * np.cos(phi)
        return x, y, z

    def entrance_x(self):
        """ Basic getter """
        return self.x_entrance

    def entrance_z(self):
        """ Basic getter """
        return self.z_entrance

    def entrance_y(self):
        """ Returns y-distance from the origin to the beginning """
        return self.y_entrance

    def entrance_radius(self):
        """ return it """
        return self.R_in

    def outrance_y(self):
        """ Returns y-distance from the origin to the finish """
        return self.y_outrance

    def plot(self, show = True):
        """ Rather simplistic single capillary plotter """
        # Get positions
        y0 = self.entrance_y()
        y1 = self.outrance_y()
        y = np.linspace(y0, y1, 200)

        # Capillary curvature
        x0 = self.local_x0(y)
        # And radius
        r0 = self.local_r0(y)

        # Plot curvature
        plt.plot(y, x0, 'k--', lw = 0.5)
        # add visibile width
        plt.plot(y, x0+r0, 'r-', lw = 1)
        plt.plot(y, x0-r0, 'r-', lw = 1)

        # Set show to False when plotting mltiple capillaries
        if show:
            # Y / X confusion is at height here
            y_min = x0.min() - 1.3 * r0.max()
            y_max = x0.max() + 1.3 * r0.max()
            print type(y_min), type(y_max)
            plt.ylim(y_min, y_max)
            plt.xlim(0, 1.1 * y1)
            plt.show()

class StraightCapillary(Capillary):
    """ Implements straight capillary parallel to the beam """
    def __init__(self, *args, **kwargs):
        """ Constructor """
        # Init parent capillary class
        Capillary.__init__(self, *args, **kwargs)

        # Set straight line factors of 5 powers 
        # Separation of bent/straight capillaries
        # could be cleaner TODO
        self.p = [self.r_entrance, 0, 0, 0, 0, 0]

        # Same concept with radius
        self.pr = [self.R_in, 0, 0]

class LinearlyTapered(StraightCapillary):
    """ You have to set the radius coefficients yourself """
    def __init__(self, *args, **kwargs):
        """ Constructor """
        self.R_out = kwargs.pop('R_out', 0.5)

        # Init parent capillary class
        StraightCapillary.__init__(self, *args, **kwargs)

        # As a default set capillary with outrance radius
        # half of the entrance radius
        self.set_rin_rout(self.R_in, self.R_out)

    def set_rin_rout(self, rin, rout):
        """ Set gradient to the radius """
        self.R_in = rin
        self.R_out = rout

        # Linear equation giving radius of position
        dR = self.R_out - self.R_in
        dY = self.outrance_y() - self.entrance_y()
        a = 1.0 * dR / dY
        b = self.R_out - self.outrance_y() * a;
        self.pr = [b, a, 0]

class BentCapillary(Capillary):
    def __init__(self, *args, **kwargs):
        """ """
        # Prepare z direction polynomial of focusing capillary
        y = kwargs.pop('y')
        D = kwargs.pop('D')
        # FIXME r_in is poorly named
        r_in = kwargs.pop('r_in')

        # TODO We want to abstract this out
        bend = kwargs.pop('bend')
        self.p = bend(r_in, y, D)

        # FIXME - this is probably no longer necessary
        # Save cartesian coordinates of capillary entrance
        # (used for directed source)
        phi = - kwargs['roll']
        self.x_entrance = r_in * np.cos(phi)
        self.z_entrance = r_in * np.sin(phi)
        kwargs.update({'x_entrance' : self.x_entrance})
        kwargs.update({'z_entrance' : self.z_entrance})

        # Prepare variable radius
        r_settings = kwargs.pop('radius')
        radius_shape = kwargs.pop('radius_shape')
        self.pr = radius_shape(y, r_settings)

        # Init parent capillary class
        Capillary.__init__(self, *args, **kwargs)

        # Those should've been appended to the kwargs probably TODO
        self.R_in = r_settings['rIn']
        self.y_entrance = y['y1']
        self.y_outrance = y['y2']

class PolyCapillaryLens(object):
    """ Multiple capillaries creator class """
    def __init__(self, **kwargs):
        """ Constructor """
        # Elements' positions in y direction
        self.y          = kwargs.pop('y_settings')
        # Lens defining diameters (in, out, max)
        self.D          = kwargs.pop('D_settings')
        # Material of capillaries
        self.material   = kwargs.pop('material', None)
        # TODO not sure if beamline has any usage
        self.beamLine   = raycing.BeamLine()

        # Capillary bend describing function
        self.bend       = bs.capillary_curvature
        # And radius changing in the y-direction
        self.radius_y   = bs.radius_curvature

    def set_structure(self, structure):
        """ Structure setter """
        self.structure = structure

    def set_bend(self, bending_function):
        """ Defines bendiness of each capillary """
        self.bend = bending_function

    def set_radius_shape(self, radius_shape_function):
        """ Defines capillary width at any point in y-direction """
        self.radius_y = radius_shape_function

    def capillary_parameters(self, r_in, roll):
        """ Prepares arguments for shape defining functions """
        # Default parameters, [xrt.BeamLine, name, position]
        args = [self.beamLine, 'bent', [0,0,0]]

        # Position of capillary in polar coordinates
        kwargs = {'roll' : roll, 'r_in' : r_in}

        # Decode lens describing parameters:
        # Physical limit in y direction
        y_entrance = self.y['y1']
        y_outrance = self.y['y2']
        kwargs.update({'y_entrance' : y_entrance})
        kwargs.update({'y_outrance' : y_outrance})

        # Capillary radius settings
        rIn = self.structure.capillary_radius()
        rOut = rIn * self.D['Dout'] / self.D['Din']
        rMax = rIn * self.D['Dmax'] / self.D['Din']
        radius = {'rIn' : rIn, 'rOut' : rOut, 'rMax' : rMax}
        kwargs.update({'radius' : radius})

        # Parameters needed for capillary shape in z direction
        kwargs.update({'y' : self.y})
        kwargs.update({'D' : self.D})

        # Material of capillary
        kwargs.update({'material' : self.material})

        # y-direction shape functions for each capillary
        kwargs.update({'bend' : self.bend})
        kwargs.update({'radius_shape' : self.radius_y})

        return args, kwargs

    def make_capillaries(self):
        """ Creates a list of OE objects """
        # Prepare containers
        self.capillaries = []

        # Generate capillaries with positions given
        # by the lens structure
        for r, phi in self.structure.polar_coordinates():
            roll = phi
            r_in = r

            # Capillary should care only about r_in and phi variable
            args, kwargs = self.capillary_parameters(r_in, roll)
            capillary = BentCapillary(*args, **kwargs)
            self.capillaries.append(capillary)

    def get_capillaries(self):
        """ get them """
        self.make_capillaries()
        return self.capillaries

    def plot(self):
        """ Visualize some of the capillaries """
        # Select capillaries on the x = 0 line
        caps = []
        EPSILON = 0.0009
        for cap in self.capillaries:
            if abs(cap.entrance_x()) < EPSILON:
                caps.append(cap)

        # Plot them onto one pyplot figure
        for cap in caps:
            cap.plot(show=False)
        plt.show()
        pass

class PolyCurveLens(object):
    """
    Concrete implementation of the real-world lenses
    with per-capillary-polynomial approach
    """
    def __init__(self, version = 'A'):
        """ You can choose *A* or *B*, see the wiki for explanation """
        # Curvature defining parameters
        self.set_version(version)

        # those are defaults
        mGlass  = rm.Material(('Si', 'O'), quantities=(1, 2), rho=2.2)
        mGold   = rm.Material('Au', rho=19.3)
        self.material = mGold
        self.structure = st.HexStructure(rIn = 0.05)

        # Capillary bend describing function
        self.bend       = bs.capillary_curvature
        # And radius changing in the y-direction
        self.radius_y   = bs.radius_curvature

    def set_version(self, version):
        """ Only A or B are currently avaiable """
        if version.lower() == 'a':
            a_y_settings = {'y0': 0.0, 'y1': 40.0,\
                            'y2': 140.0, 'yf': 155.0,\
                            'ym': 88.0}
            a_D_settings = {'Din': 4.5, 'Dmax': 8.0, 'Dout': 2.4}
            self.y_settings = a_y_settings
            self.D_settings = a_D_settings
            print 'version set to A'
            return
        if version.lower() == 'b':
            b_y_settings = {'y0': 0.0, 'y1': 25.0,\
                            'y2': 91.5, 'yf': 94.0,\
                            'ym': 55.0}
            b_D_settings = {'Din': 2.75, 'Dmax': 4.4, 'Dout': 1.1}
            self.y_settings = b_y_settings
            self.D_settings = b_D_settings
            print 'version set to B'
            return

        # Bad input case:
        print 'Please set lens version to \'A\' or \'B\' only'

    def set_bend_function(self, bend_function):
        """ Capillary curvature polynomial coefficients generator """
        self.bend = bend_function

    def y_entrance(self):
        """ Beginning of the lens in y-direction """
        return self.y_settings['y1']

    def set_structure(self, structure):
        """ See elements.structures.LensStructure for type description """
        self.structure = structure

    def set_material(self, material):
        """ This must be a xrt.material object """
        self.material = material

    def get_capillaries(self):
        """ This returns the final product """
        # Create lens
        lens = PolyCapillaryLens(y_settings=self.y_settings,\
                                 D_settings=self.D_settings,\
                                 material=self.material)
        # Add structure
        lens.set_structure(self.structure)

        # And y-direction shape for each capillary
        lens.set_bend(self.bend)
        lens.set_radius_shape(self.radius_y)

        return lens.get_capillaries()

