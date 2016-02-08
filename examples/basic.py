# TODO this should be in some kind of settings.py
_processes = 8
_threads = 1

import numpy as np
import multiprocessing as mp
import os
from datetime import datetime as dt
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

        # Self-referencing via the beamline allows
        # the usage of class specific methods within the run_process
        self.beamLine.self = self

        # TODO Make this auto-adjustable
        self.savefolder = 'data_b'

        # Set of OE objects capable of multiple_reflections
        self.capillaries = []

        # Container for xrt::plots
        self.plots = []

        # Photon container
        self.beamTotal = None

        # Source dimensions
        self.x_size = 1
        self.z_size = 1

        # Source divergence
        self.x_divergence = 0.01
        self.z_divergence = 0.01

        # Source energy parameters
        self.distE = 'normal'
        self.energies = (9000, 100)

        # Number of photons in one iteration of one thread
        self.nrays = 100

        # Number of iterations
        self.repeats = 4

    def set_capillaries(self, caps):
        """ do it """
        self.capillaries = caps
        self.beamLine.capillaries = caps
        print 'Number of capillaries: ', len(caps)
        radius = caps[0].entrance_radius()
        self.x_size = self.z_size = radius/2.0

    def set_nrays(self, rays):
        """ rays per shot into the capillary """
        self.nrays = rays

    def set_repeats(self, peats):
        """ adjust with the number of cores available """
        self.repeats = peats

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
            # FIXME something wrong with y-distributions
            self.beamLine,'Fitted',(0,39.99,0), nrays=nrays,
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
                hitpoint = [cap.entrance_x(),
                            cap.entrance_y(),
                            cap.entrance_z()]

                light = self.source.shine(hitpoint)

                # Push through
                beamLocal, _ = cap.multiple_reflect(light,\
                                        maxReflections=550)

                # TODO filter_good() here might be worth trying

                # Hold photons for export
                if self.beamTotal is None:
                    self.beamTotal = beamLocal
                else:
                    self.beamTotal.concatenate(beamLocal)

            out = {}
            return out

        # XRT internals
        rr.run_process = local_process

    def local_filepath(self, process_id):
        """ Generate unique files for keeping photons
            generated in separate processes """
        filepath = self.savefolder + '/process{}.csv'.format(process_id)
        return filepath

    @staticmethod
    def local_process(beamLine, shineOnly1stSource=False):
        """ raycing.run_process must be overriden globally """
	# Debug info
        process_id = mp.current_process()._identity[0]
	debug_start = 'Prcoess {} started at: {}.'
        print debug_start.format(process_id , dt.now())

        for it, cap in enumerate(beamLine.capillaries):
            hitpoint = [cap.entrance_x(),
                        cap.entrance_y(),
                        cap.entrance_z()]

            light = beamLine.sources[0].shine(hitpoint)

            # Push through
            beamLocal, _ = cap.multiple_reflect(light,\
                                    maxReflections=550)

            # We wan't to keep only alive photons
            beamLocal.filter_good()

            # After each capillary write to csv file
            frame = ub.make_dataframe(beamLocal)
            filepath = beamLine.self.local_filepath(process_id)

            # Add header only when creating the file
            header_needed = not os.path.isfile(filepath)
            frame.to_csv(filepath, mode='a', header=header_needed)

	    if it%1000 is 0:
		debug_inside = 'Capillary {} done at process {} in time {}'
		print debug_inside.format(it, process_id, dt.now())

	# More debug
	debug_finish = 'Prcoess {} finished at: {}.'
        print debug_finish.format(process_id, dt.now())

        out = {}
        return out

    def run_it(self):
        """ do it """
        self.make_source()
        # self.make_run_process()
        self.beamTotal = None

        xrtr.run_ray_tracing(self.plots,
                            repeats=self.repeats,\
                            beamLine=self.beamLine,\
                            processes=_processes,\
                            threads=_threads)

    def get_source(self):
        """ it's free """
        return self.source

    def get_beam(self):
        """ get it """
        return ub.beam_from_csvs(self.savefolder)

def test_lens(photons, capillaries):
    """ Perform ray traycing """
    test = MultipleCapillariesTest()
    test.set_beam(photons)
    test.set_capillaries(capillaries)
    test.run_it()

    return test

