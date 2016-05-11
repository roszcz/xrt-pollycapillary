import numpy as np
from utils import plotter as up

import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs

class FitGeometricSource(rs.GeometricSource):
    """ Special source generating photons exactly at the
    capillary entrance """
    def __init__(self, *args, **kwargs):
        """ Nothing different from the original constructor """
        rs.GeometricSource.__init__(self, *args, **kwargs)

    def shine(self, hitpoint = (0,10,0)):
        """ Source special logic, shine in direction defined by hitpoint"""
        # Obsolete parameters used by the original shine() method
        toGlobal = True
        withAmplitudes = False
        accuBeam = None

        # Prepare beam to be returned
        bo = rs.Beam(self.nrays,
                     withAmplitudes=withAmplitudes)
        bo.state[:] = 1

        self._apply_distribution(bo.y, self.disty, self.dy)

        # TODO Add normal distribution!
        # We want to shine a flat distribution
        # around the capillary entrance point
        xMin, xMax = hitpoint[0] - self.dx, hitpoint[0] + self.dx
        bo.x = np.random.uniform(xMin, xMax, self.nrays)

        zMin, zMax = hitpoint[2] - self.dz, hitpoint[2] + self.dz
        bo.z = np.random.uniform(zMin, zMax, self.nrays)

        # Likewise we want the momentum to be distributed
        # around the direction of the capillary entrance

        # Only direction of momentum can be specified
        # so normalization is mandatory
        normfactor = np.sqrt(sum([x**2 for x in hitpoint]))

        # With momentum distribution in the x-direction ...
        a0 = 1. * hitpoint[0] / normfactor
        aMin, aMax = a0 - self.dxprime, a0 + self.dxprime
        bo.a = np.random.uniform(aMin, aMax, self.nrays)

        #  ... and in the z-direction ...
        c0 = 1. * hitpoint[2] / normfactor
        cMin, cMax = c0 - self.dzprime, c0 + self.dzprime
        bo.c = np.random.uniform(cMin, cMax, self.nrays)

        # ... we can find the momentum distribution in the y-direction
        ac = bo.a**2 + bo.c**2
        if sum(ac > 1) > 0:
            bo.b[:] = (ac + 1)**0.5
            bo.a[:] /= bo.b
            bo.c[:] /= bo.b
            bo.b[:] = 1.0 / bo.b
        else:
            bo.b[:] = (1 - ac)**0.5

        # This assumes that distE is not None
        bo.E[:] = rs.make_energy(self.distE, self.energies,\
                                 self.nrays, self.filamentBeam)

        # Add a container for number of reflections for each ray
        bo.nRefl = np.zeros_like(bo.state)

        # So far we neglect polarization, but it's needed
        # for xrt compatibility
        rs.make_polarization(self.polarization, bo, self.nrays)

        # This assumes toGlobal is True
        raycing.virgin_local_to_global(self.bl, bo, self.center)

        return bo

class FitGeometricTest(object):
    """ Testing class for the specific source type """
    def __init__(self):
        """ Constructore """
        # Set defaults
        # Source parameters
        self.nrays       = 100000
        self.distE       = 'normal'
        self.energies    = (9000, 100)
	self.position	 = [0, 0, 0]
        # x-direction
        self.distx       = 'flat'
        self.dx          = 1
        self.distxprime  = 'flat'
        self.dxprime     = 0.1
        # z-direction
        self.distz       = 'flat'
        self.dz          = 1
        self.distzprime  = 'flat'
        self.dzprime     = 0.1

        # Create default source
        self.make_source()

    def set_dx(self, val):
        """ dx setter """
        self.dx = val

    def set_source_position(self, where):
	""" Position in XYZ space """
	self.position = where

    def set_dz(self, val):
        """ dz setter """
        self.dz = val

    def set_dxprime(self, val):
        """ dxprime setter """
        self.dxprime = val

    def set_dzprime(self, val):
        """ dzprime setter """
        self.dzprime = val

    def set_energy_distribution(self, dist):
        """ Type of energy distribution normal/lines """
        self.distE = dist

    def set_energies(self, energies):
        """ Set energy distribution parameters """
        self.energies = energies

    def make_source(self):
        """ Creates source with current settings """
        beamLine = raycing.BeamLine()
        self.source = FitGeometricSource(
                beamLine,'source',
		self.position,
                nrays	    = self.nrays,
		distx	    = self.distx,
                dx	    = self.dx,
                distxprime  = self.distxprime,
                dxprime	    = self.dxprime,
                distz	    = self.distz,
                dz	    = self.dz,
                distzprime  = self.distzprime,
                dzprime	    = self.dzprime,
                distE	    = self.distE,
                energies    = self.energies,
                polarization=None)

    def shine(self, direction = [0, 1, 0]):
        """ Generate photons """
	self.make_source()
        return self.source.shine(direction)

    def run_test(self):
        """ Show example results """
        self.make_source()
        beam = self.source.shine([1, 1, 1])
        beam.concatenate(self.source.shine([1, 1, -1]))

        bp = up.BeamPlotter(beam)
        bp.show(1)
        bp.show(10)

class GeometricSourceTest(object):
    """ Class used for testing the original xrt-source object and its parameters """
    def __init__(self):
	""" Constructor """
        # Set defaults
        # Source parameters
	self.position	 = [0, 0, 0]
        self.nrays       = 100000
        self.distE       = 'normal'
        self.energies    = (9000, 100)
        # x-direction
        self.distx       = 'flat'
        self.dx          = 1
        self.distxprime  = 'flat'
        self.dxprime     = 0.1
        # z-direction
        self.distz       = 'flat'
        self.dz          = 1
        self.distzprime  = 'flat'
        self.dzprime     = 0.1

        # Create default source
        self.make_source()

    def make_source(self):
        """ Creates source with current settings """
        beamLine = raycing.BeamLine()
        self.source = rs.GeometricSource(
                beamLine,'source',
		self.position,
                nrays	    = self.nrays,
		distx	    = self.distx,
                dx	    = self.dx,
                distxprime  = self.distxprime,
                dxprime	    = self.dxprime,
                distz	    = self.distz,
                dz	    = self.dz,
                distzprime  = self.distzprime,
                dzprime	    = self.dzprime,
                distE	    = self.distE,
                energies    = self.energies,
                polarization=None)

    def shine(self):
        """ Generate photons """
	self.make_source()
        return self.source.shine()

    def set_dx(self, val):
        """ dx setter """
        self.dx = val

    def set_source_position(self, where):
	""" Position in XYZ space """
	self.position = where

    def set_dz(self, val):
        """ dz setter """
        self.dz = val

    def set_dxprime(self, val):
        """ dxprime setter """
        self.dxprime = val

    def set_dzprime(self, val):
        """ dzprime setter """
        self.dzprime = val

    def set_energy_distribution(self, dist):
        """ Type of energy distribution normal/lines """
        self.distE = dist

    def set_energies(self, energies):
        """ Set energy distribution parameters """
        self.energies = energies


def test_it():
    """ Check if compiles """
    # Source parameters
    nrays       = 10000
    distE       = 'normal'
    energies    = (9000, 100)
    # x-direction
    distx       = 'flat'
    dx          = 1
    distxprime  = 'flat'
    dxprime     = 0.1
    # z-direction
    distz       = 'flat'
    dz          = 1
    distzprime  = 'flat'
    dzprime     = 0.1

    beamLine = raycing.BeamLine()
    src = FitGeometricSource(
            beamLine,'source',(0,0,0), nrays=nrays,
            distx=distx, dx=dx, distxprime=distxprime, dxprime=dxprime,
            distz=distz, dz=dz, distzprime=distzprime, dzprime=dzprime,
            distE=distE, energies=energies,
            polarization=None)

    # Shine from one point
    yo = src.shine((1, 40, -1))
    # and from some other
    yo.concatenate(src.shine((-1, 40, 1)))

    return yo
