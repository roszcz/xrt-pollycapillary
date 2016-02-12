import os
import numpy as np
import matplotlib.pyplot as plt
from elements import capillary as ec
from elements import structures as st
from lenses import polycapillary as lp
from utils import plotter as up
from utils import beam as ub
from examples import basic as eb
from examples import source as es

import xrt.backends.raycing.run as rr

def create_source():
    """ Generate photons with xrt and save resulting beam """
    # Every source detail is set and tested within it's module
    # so here we can just create the beam at the desired moment
    beamGlobalTotal = es.create_geometric(1e5)
    ub.save_beam_compressed(beamGlobalTotal, 'basic_source.beamc')

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
    structure = st.CakePiece(rIn = 0.02,\
                                nx_capillary = 27,\
                                ny_bundle = 15,\
                                angle = np.pi/24.0)
    lens.set_structure(structure)

    return lens

def create_beam(dirname):
    """ Generates csv files filled with photons inside the dirname directory """
    # Set stuff above
    lens = create_lens()
    caps = lens.get_capillaries()

    # Preparation
    setup = eb.MultipleCapillariesFittedSource()
    setup.set_capillaries(caps)
    # Number of photons per run per capillary
    setup.set_nrays(50)
    # Number of runs
    setup.set_repeats(16)
    # Photon storage directory
    setup.set_folder(dirname)

    setup.run_it()

    return True


# This is not pretty, yet obligatory
rr.run_process = eb.MultipleCapillariesFittedSource.local_process

if __name__ == '__main__':
    """ python main.py """

    # Remove dead photons
    # ceam = setup.get_beam()

    # Choose path for storage
    directory = 'huge_bend'

    # Create if necessary
    if not os.path.exists(directory):
        os.makedirs(directory)

        # Run ray traycing (LONG) only if no such directory exist
        create_beam(directory)
    else :
        print "Directory exists, photon storage not possible in pre-existing directories"

    # FIXME this name is bleh
    beam = ub.beam_from_csvs(directory)

    # Show results
    bp = up.BeamPlotter(beam)
    bp.set_limits([-5,5])
    bp.set_save_name('png/example_140.png')
    bp.show(140)
    bp.set_save_name('png/example_155.png')
    bp.show(155)
    bp.set_save_name('png/example_170.png')
    bp.show(170)
