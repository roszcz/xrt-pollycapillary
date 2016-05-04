import os
import itertools
import numpy as np
import multiprocessing as mp
from datetime import datetime as dt

import xrt.runner as xrtr
import xrt.plotter as xrtp
import xrt.backends.raycing.run as rr
import xrt.backends.raycing as raycing
import xrt.backends.raycing.sources as rs
import xrt.backends.raycing.screens as rsc

from utils import beam as ub
from elements import sources as es

class MultipleCapillaries(object):
    """ Abstract class for xrt setups with multiple capillaries """
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

        # Machine dependent
        # FIXME setting 1 is currently a no-go due to 
        # mp.Process not having a iterable id
        # and _identity[0] throws an error
        self.processes = 2

        # Container for xrt::plots
        self.plots = []

        # Source 3D position
        self.source_position = [0, 0, 0]

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

        print 'Setup no contains {} capillaries'.format(len(caps))

        # Used for source fitting
        radius = caps[0].entrance_radius()
        self.x_size = self.z_size = radius/2.0

        # Position the source at the lens entrance
        # (-0.01 is for numerical safety FIXME)
        source_ent = caps[0].entrance_y() - 0.01
        self.source_position = [0, caps[0].entrance_y(), 0]

    def set_nrays(self, rays):
        """ rays per shot into the capillary """
        self.nrays = rays

    def set_repeats(self, peats):
        """ adjust with the number of cores available """
        self.repeats = peats

    def set_processes(self, howmany):
        """ Consult with Your number of cores """
        self.processes = howmany

    def set_folder(self, dirname):
	""" progress over protocol """
	self.savefolder = dirname

    def set_dxprime(self, value):
        """ x-direction divergence """
        self.x_divergence = value

    def set_dzprime(self, value):
        """ z-direction divergence """
        self.z_divergence = value

    def make_source(self):
        """ This should be setup-specific """
        pass

    def local_filepath(self, process_id):
        """ Generate unique files for keeping photons
            generated in separate processes """
        filepath = self.savefolder + '/process{}.csv'.format(process_id)
        return filepath

    @staticmethod
    def local_process(beamLine, shineOnly1stSource=False):
        """ Override this method in Your setup """
        pass

    def run_it(self):
        """ do it """
        self.make_source()
        # self.make_run_process()
        self.beamTotal = None

        # FIXME this actually is obsolete
        # and process managing should be done in some
        # simpler way than xrt is handling it atm
        # 
        xrtr.run_ray_tracing(self.plots,
                            repeats=self.repeats,\
                            beamLine=self.beamLine,\
                            processes=self.processes)

    def get_source(self):
        """ it's free """
        return self.source

    def get_beam(self):
        """ get it """
        return ub.load_beam(self.savefolder)

class MultipleCapillariesFittedSource(MultipleCapillaries):
    """ Each capillary has its own light source just at the entrance """
    def make_source(self):
        """ Prepare source parameter """
        # Source parameters
        position    = self.source_position
        # Number of photons per run
        nrays       = self.nrays
        # Energy distribution
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
            self.beamLine, 'Fitted', position, nrays=nrays,
            distx=distx, dx=dx, distxprime=distxprime, dxprime=dxprime,
            distz=distz, dz=dz, distzprime=distzprime, dzprime=dzprime,
            distE=distE, energies=energies,
            polarization=self.polarization)

    @staticmethod
    def local_process(beamLine, shineOnly1stSource=False):
        """ raycing.run_process must be overriden globally """
	# Debug info
        process_id = mp.current_process()._identity[0]
	debug_start = 'Prcoess {} started at: {}.'
        print debug_start.format(process_id , dt.now())

        # For every capillary
        for it, cap in enumerate(beamLine.capillaries):
            hitpoint = [cap.entrance_x(),
                        cap.entrance_y(),
                        cap.entrance_z()]

            # shine directly into its center
            light = beamLine.sources[0].shine(hitpoint)

            # and perform reflections
            beamLocal, _ = cap.multiple_reflect(light,\
                                    maxReflections=550)

            # We wan't to keep only alive photons
            # TODO but we need to know how many were generated!
            beamLocal.filter_good()

            # After each capillary write to csv file
            frame = ub.make_dataframe(beamLocal)
            filepath = beamLine.self.local_filepath(process_id)

            # Add header only when creating the file
            header_needed = not os.path.isfile(filepath)
            frame.to_csv(filepath, mode='a', header=header_needed)

            # Every 100 capillaries inform user about progress
	    if it%100 is 0:
		debug_inside = 'Capillary {} done at process {} in time {}'
		print debug_inside.format(it, process_id, dt.now())

	# Inform user that this run is over
	debug_finish = 'Prcoess {} finished at: {}.'
        print debug_finish.format(process_id, dt.now())

        # Return empty dict for xrt compability
        out = {}
        return out

class MultipleCapillariesNormalSource(MultipleCapillaries):
    """ One source shining into all of the capillaries """
    def make_source(self):
        """ Prepare source parameter """
        # Source parameters
        position    = self.source_position
        # Number of photons per run
        nrays       = self.nrays
        # Energy distribution
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

        self.source = rs.GeometricSource(\
            # FIXME something wrong with y-distributions
            self.beamLine, 'Fitted', position, nrays=nrays,
            distx=distx, dx=dx, distxprime=distxprime, dxprime=dxprime,
            distz=distz, dz=dz, distzprime=distzprime, dzprime=dzprime,
            distE=distE, energies=energies,
            polarization=self.polarization)

    @staticmethod
    def local_process(beamLine, shineOnly1stSource=False):
        """ raycing.run_process must be overriden globally """
	# Debug info
        process_id = mp.current_process()._identity[0]
	debug_start = 'Prcoess {} started at: {}.'
        print debug_start.format(process_id , dt.now())

        # Shine once per run
        light = beamLine.sources[0].shine()

        # For every capillary
        for it, cap in enumerate(beamLine.capillaries):
            hitpoint = [cap.entrance_x(),
                        cap.entrance_y(),
                        cap.entrance_z()]

            # Perform reflections
            beamLocal, _ = cap.multiple_reflect(light,\
                                    maxReflections=550)

            # We wan't to keep only alive photons
            # TODO but we need to know how many were generated!
            beamLocal.filter_good()

            # After each capillary write to csv file
            frame = ub.make_dataframe(beamLocal)
            filepath = beamLine.self.local_filepath(process_id)

            # Add header only when creating the file
            header_needed = not os.path.isfile(filepath)
            frame.to_csv(filepath, mode='a', header=header_needed)

            # Every 100 capillaries inform user about progress
	    if it%100 is 0:
		debug_inside = 'Capillary {} done at process {} in time {}'
		print debug_inside.format(it, process_id, dt.now())

	# Inform user that this run is over
	debug_finish = 'Prcoess {} finished at: {}.'
        print debug_finish.format(process_id, dt.now())

        # Return empty dict for xrt compability
        out = {}
        return out
