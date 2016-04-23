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
from elements import structures as es

from setups import firstlens as fl

import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.run as rr

def create_beam(dirname):
    """ Generates csv files filled with photons inside the dirname directory """
    # Create folder if necessary
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    else:
        print 'Directory exists, using it anyway'

    # Prepare lens curvature
    lens = lp.PolyCurveLens('A')

    # Prepare a single capillary at x=1, y=1 [mm] position
    # with entrance radius 0.1
    single = es.Singular(1, 1, 0.1)

    # Prepare ray-traycing
    lens.set_structure(single)
    caps = lens.get_capillaries()
    setup = fl.MultipleCapillariesFittedSource()
    setup.set_capillaries(caps)

    # Number of photons per run per capillary
    setup.set_nrays(8000)
    # Number of avaiable cores
    setup.set_processes(8)
    # Number of runs
    setup.set_repeats(128)

    # Photon storage dirctory
    setup.set_folder(dirname)

    setup.run_it()

    return True

# FIXME
# This is not pretty, yet obligatory (only for beam creation)
rr.run_process = fl.MultipleCapillariesFittedSource.local_process

if __name__ == '__main__':
    """ console$: python main.py """
    # Creating example beam from default lens-A object
    create_beam('example_lens')
