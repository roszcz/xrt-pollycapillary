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
    structure = st.HexStructure(rIn = 0.2,\
                                nx_capillary = 7,\
                                ny_bundle = 5)
    lens.set_structure(structure)

    return lens

# This is not pretty, yet obligatory
rr.run_process = eb.MultipleCapillariesFittedSource.local_process

if __name__ == '__main__':
    """ python main.py """
    # Create 10000 photons
    # beam = es.create_geometric(1e4)

    # Set stuff above
    lens = create_lens()
    caps = lens.get_capillaries()

    # Preparation
    setup = eb.MultipleCapillariesFittedSource()
    setup.set_capillaries(caps)
    # Number of photons per run per capillary
    setup.set_nrays(10)
    # Number of runs
    setup.set_repeats(4)

    setup.run_it()

    # You can use this in IPython with single capillaries
    # source = setup.get_source()

    # Remove dead photons
    ceam = setup.get_beam()

    # Save for research
    # ub.save_beam_compressed(ceam, 'far_capillaries.beamc')

    # Show results
    # ub.show_beam(ceam)
    bp = up.BeamPlotter(ceam)
    # bp.set_limits([-4,4])
    bp.set_save_name('png/example_140.png')
    bp.show(140)
    bp.set_save_name('png/example_155.png')
    bp.show(155)
    bp.set_save_name('png/example_170.png')
    bp.show(170)
