import matplotlib.pyplot as plt
from elements import source as es
from elements import capillary as ec
from elements import structures as st
from lenses import polycapillary as lp
from utils import beam as ub
from examples import basic as eb

def create_source():
    """ Generate photons with xrt and save resulting beam """
    # Every source detail is set and tested within it's module
    # so here we can just create the desired object 
    beamGlobalTotal = es.create_geometric()

    # And it only needs to be done once, after that ...
    ub.save_beam_compressed(beamGlobalTotal, 'basic_source.beam')

def load_source():
    """ Load beam from file saved with the above function """
    # ... we can operate on photons loaded from the hard drive
    loaded_beam = ub.load_beam_compressed('basic_source.beamc')

    return loaded_beam

if __name__ == '__main__':
    """ python main.py """
    # Create 10000 photons
    beam = es.create_geometric(1e6)

    # Lens parameters needed for capillary shape calculations
    y_settings = {'y0': 0.0, 'y1': 40.0,\
                  'y2': 140.0, 'yf': 155.0,\
                  'ym': 88.0}
    D_settings = {'Din': 4.5, 'Dmax': 8.0, 'Dout': 2.4}

    lens = lp.PolyCapillaryLens(y_settings=y_settings,\
                                D_settings=D_settings)
    structure = st.HexStructure(rIn = 0.01,\
                                nx_capillary = 9,\
                                ny_bundle = 11)
    lens.set_structure(structure)

    # This is it
    caps = lens.get_capillaries()
    ub.move_beam_to(beam, 39.99)

    # FIXME nRefl somehow doesn't work!
    test = eb.test_lens(beam, caps)
    ceam = test.get_beam()

    # Show the beam right after the capillaries
    ceam.filter_good()
    ub.show_beam(ceam)

