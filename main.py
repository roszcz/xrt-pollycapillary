# FIXME still not effective
import matplotlib as mpl
mpl.use('Agg')

import os
import numpy as np
import matplotlib.pyplot as plt
from elements import capillary as ec
from elements import structures as st
from lenses import polycapillary as lp
from utils import plotter as up
from utils import beam as ub
from utils import cutter as uc
from examples import source as es

from setups import firstlens as fl

import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.run as rr

def create_beam(dirname):
    """ Generates csv files filled with photons inside the dirname directory """
    # Create folder if necessary
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Prepare lens and capillaries within
    lens = lp.PolyCurveLens('A')
    caps = lens.get_capillaries()

    # Preparation
    setup = fl.MultipleCapillariesFittedSource()
    setup.set_capillaries(caps)

    # TODO this might work as
    # setup.set_total_number_of_photons(8000*8*156)
    # Number of photons per run per capillary
    setup.set_nrays(800)
    # Number of avaiable cores
    setup.set_processes(2)
    # Number of runs
    setup.set_repeats(6)

    # Photon storage dirctory
    setup.set_folder(dirname)

    setup.run_it()

    return True

def show_beam(folder):
    """ Show beam from folder """
    beam = ub.load_beam(folder)

    # Show results
    bp = up.BeamPlotter(beam)
    bp.set_limits(None)
    bp.set_save_name('png/example_140.png')
    bp.show(140)
    bp.set_save_name('png/example_155.png')
    bp.show(155)
    bp.set_save_name('png/example_170.png')
    bp.show(170)

def show_or_create(directory):
    """ Example usage """
    # Create if necessary
    if not os.path.exists(directory):
        os.makedirs(directory)

        # Run ray traycing (LONG) only if no such directory exist
        create_beam(directory)
        print "Beam created, goodbye"
    else :
        print "Directory exists, photon storage not possible in pre-existing directories"
        print "Trying to load from that directory"
        show_beam(directory)

def create_defects(directory):
    """ Example run with lens-defects """
    print 'Loading... wait'
    beam = ub.load_beam(directory)

    # Create defects
    beam = uc.create_defects(beam, 21)
    cp = up.BeamPlotter(beam)
    cp.set_save_name('png/defects_140.png')
    cp.set_limits([-3, 3])
    cp.show(140)
    print 'Defects done'

    # Propagate light
    ub.move_beam_to(beam, 155)

    # Object interaction
    deam = uc.make_wires(beam, 0.077)

    # Save as png, only at the detector
    dp = up.BeamPlotter(deam)
    # cp.set_save_name('png/triangle_at_focal_155.png'.format(position))
    # cp.set_limits([-0.5, 0.5])
    # cp.show(155)
    cp.set_save_name('png/defects_170.png')
    cp.set_limits([-3, 3])
    cp.show(170)

# FIXME
# This is not pretty, yet obligatory (only for beam creation)
rr.run_process = fl.MultipleCapillariesFittedSource.local_process

if __name__ == '__main__':
    """ console$: python main.py """
    # Creating example beam from default lens-A object
    create_beam('example_lens')
