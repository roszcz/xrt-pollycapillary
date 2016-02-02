# TODO this should be in some kind of settings.py
_processes = 1

import numpy as np
import itertools

import xrt.runner as xrtr
import xrt.backends.raycing.screens as rsc
import xrt.plotter as xrtp
import xrt.backends.raycing.run as rr
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing as raycing

from elements import sources as es
from utils import beam as ub

class MultipleCapillariesTest(object):
    """ Use photons loaded from the hard drive """
    def __init__(self):
        """ ,.-`''`-., """
        # Obligatory beamline to use xrt functionality
        self.beamLine = raycing.BeamLine()

        # Photon container
        self.beamTotal = None

        # Parallelization helpers
        self.beam_iterator = itertools.count()
        self.beam_chunk_size = 1000

        # Init capillaries container to an empty one
        # Capillaries might easily be created within this test ???
        self.capillaries = []

        # No plots by default
        self.plots = []

    def set_beam(self, photons):
        """ Load previously generated photons """
        self.source_beam = photons
        # Reset counter
        self.beam_iterator = itertools.count()

    def set_capillaries(self, caps):
        """ simple """
        self.capillaries = caps

    def make_run_process(self):
        """ Obligatory overload, all logic is handled here """
        def local_process(beamLine, shineOnly1stSource=False):
            # This has to conserve the atomicity of the operation!
            local_it = self.beam_iterator.next()
            rnga = local_it * self.beam_chunk_size
            rngb = (local_it + 1) * self.beam_chunk_size

            # Debug
            print 'Taking beam from', rnga, 'to', rngb

            # This acts as xrt::shine()
            beam = ub.copy_by_index(self.source_beam, range(rnga, rngb))

            # TODO plenty place for optimalization is probably here
            for cap in self.capillaries:
                # Get a part of beam hitting this capillary
                hitpoint = [cap.entrance_x(), cap.entrance_z()]
                beam_part = ub.get_beam_part(beam,\
                                             hitpoint,\
                                             cap.entrance_radius())
                # Multiple reflect
                beamLocal, _ = cap.multiple_reflect(beam_part,\
                                            maxReflections=50)

                # Hold photons for export
                if self.beamTotal is None:
                    self.beamTotal = beamLocal
                else:
                    self.beamTotal.concatenate(beamLocal)

            # Return a empty dictionary for xrt 
            out =  {}
            return out

        # XRT internals
        rr.run_process = local_process

    def run_it(self):
        """ """
        self.make_run_process()

        # We want to go through the whole beam
        # Provide shorter beam if You fancy otherwise
        _repeats = np.ceil(self.source_beam.x.size / self.beam_chunk_size)

        xrtr.run_ray_tracing(self.plots,
                            repeats=_repeats,\
                            beamLine=self.beamLine,\
                            processes=_processes)

    def get_beam(self):
        """ Results """
        return self.beamTotal

class MultipleCapillariesFittedSource(object):
    """ Generate photons on the run """
    def __init__(self):
        """ Constructor """
        # Obligatory beamline to use xrt functionality
        self.beamLine = raycing.BeamLine()

        self.capillaries = []

        self.plots = []

        # Photon container
        self.beamTotal = None

        # TODO We might want setters for all of these
        # Source dimensions
        self.x_size = 1
        self.z_size = 1

        # Source divergence
        self.x_divergence = 0.1
        self.z_divergence = 0.1

        # Source energy parameters
        self.distE = 'normal'
        self.energies = (9000, 100)

        # Number of photons in one iteration of one thread
        self.nrays = 100

    def set_capillaries(self, caps):
        """ do it """
        self.capillaries = caps
        radius = caps[0].entrance_radius()
        self.x_size = self.z_size = radius/2.0

    def make_source(self):
        """ Prepare source parameter """

        # Source parameters
        nrays       = self.nrays
        distE       = self.distE
        energies    = self.energies
        # x-direction
        distx       = 'flat'
        dx          = self.x_size
        distxprime  = 'flat'
        dxprime     = self.x_divergence
        # z-direction
        distz       = 'flat'
        dz          = self.z_size
        distzprime  = 'flat'
        dzprime     = self.z_divergence

        self.polarization = None

        self.source = es.FitGeometricSource(\
            self.beamLine,'Fitted',(0,39.9,0), nrays=nrays,
            distx=distx, dx=dx, distxprime=distxprime, dxprime=dxprime,
            distz=distz, dz=dz, distzprime=distzprime, dzprime=dzprime,
            distE=distE, energies=energies,
            polarization=self.polarization)

    def make_run_process(self):
        """ """
        def local_process(beamLine, shineOnly1stSource=False):
            # Iterate over the capillaries
            # and shine() into each of them
            for cap in self.capillaries:
                # FIXME no hardcoded position please
                hitpoint = [cap.entrance_x(), 40, cap.entrance_z()]
                beam = self.source.shine(hitpoint)

                # Push through
                beamLocal, _ = cap.multiple_reflect(beam,\
                                        maxReflections=50)

                # Hold photons for export
                if self.beamTotal is None:
                    self.beamTotal = beamLocal
                else:
                    self.beamTotal.concatenate(beamLocal)

            out = {}
            return out

        # XRT internals
        rr.run_process = local_process

    def run_it(self):
        """ do it """
        self.make_source()
        self.make_run_process()
        self.beamTotal = None

        # TODO get rid of this
        _repeats = 10

        xrtr.run_ray_tracing(self.plots,
                            repeats=_repeats,\
                            beamLine=self.beamLine,\
                            processes=_processes)

    def get_source(self):
        """ it's free """
        return self.source

    def get_beam(self):
        """ get it """
        return self.beamTotal

def test_lens(photons, capillaries):
    """ Perform ray traycing """
    test = MultipleCapillariesTest()
    test.set_beam(photons)
    test.set_capillaries(capillaries)
    test.run_it()

    return test

