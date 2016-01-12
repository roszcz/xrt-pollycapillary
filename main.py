import matplotlib.pyplot as plt
from elements import source
from utils import beam as ub

def create_source():
    """ Generate photons with xrt and save resulting beam """
    # Every source detail is set and tested within it's module
    # so here we can just create the desired object 
    beamGlobalTotal = source.create_geometric()

    # And it only needs to be done once, after that ...
    ub.save_beam_compressed(beamGlobalTotal, 'basic_source.beam')

def load_source():
    """ Load beam from file saved with the above function """
    # ... we can operate on photons loaded from the hard drive
    loaded_beam = ub.load_beam_compressed('global_total.beamc')

    return loaded_beam

if __name__ == '__main__':
    """ python main.py """
    # Read from file, see above
    photons = load_source()

    # For example show first 1000 of photons' positions
    howmany = 1000

    # Plot
    plt.scatter(photons.x[:howmany], photons.z[:howmany])
    plt.show()
