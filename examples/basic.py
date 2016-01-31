
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

from utils import beam as ub

class MultipleCapillariesTest(object):
    """ Push photons through a set of capillaries """
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

def test_lens(photons, capillaries):
    """ Perform ray traycing """
    test = MultipleCapillariesTest()
    test.set_beam(photons)
    test.set_capillaries(capillaries)
    test.run_it()

    return test

