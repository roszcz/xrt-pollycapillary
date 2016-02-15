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

import xrt.backends.raycing.run as rr

def create_lens():
    """ Wrapped lens creation """
    # Lens parameters needed for capillary shape calculations
    y_settings = {'y0': 0.0, 'y1': 40.0,\
                  'y2': 140.0, 'yf': 155.0,\
                  'ym': 88.0}
    D_settings = {'Din': 4.5, 'Dmax': 8.0, 'Dout': 2.4}

    # This is used to control capillaries' curvature
    lens = lp.PolyCapillaryLens(y_settings=y_settings,\
                                D_settings=D_settings)
    structure = st.HexStructure(rIn = 0.02,\
                                nx_capillary = 2,\
                                ny_bundle = 1)
    lens.set_structure(structure)

    return lens

def create_beam(dirname):
    """ Generates csv files filled with photons inside the dirname directory """
    # Set stuff above
    lens = create_lens()
    caps = lens.get_capillaries()

    # Preparation
    setup = fl.MultipleCapillariesFittedSource()
    setup.set_capillaries(caps)
    # Number of photons per run per capillary
    setup.set_nrays(50)
    # Number of avaiable cores
    setup.set_processes(2)
    # Number of runs
    setup.set_repeats(16)
    # Photon storage directory
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


# This is not pretty, yet obligatory
rr.run_process = fl.MultipleCapillariesFittedSource.local_process

if __name__ == '__main__':
    """ python main.py """

    # Choose path for storage
    directory = 'data'
    beam = ub.load_beam(directory)

    # Positions to create the wires at
    positions = [154 + 0.1 * it for it in range(21)]

    for position in positions:
        print "Trying to simulate a bunch of wires at:", position
        # Propagate light
        ub.move_beam_to(beam, position)

        # Cut the wires out
        ceam = uc.make_wires(beam)

        # Save as png, only at the detector
        cp = up.BeamPlotter(ceam)
        cp.set_save_name('png/wire_at_{}.png'.format(position))
        cp.set_limits([-3, 3])
        cp.show(170)
