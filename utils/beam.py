import pickle
import gzip
import matplotlib.pyplot as plt
import xrt.backends.raycing.sources as rs

def move_beam_to(beam, where):
    """ Propagates the beam in vacum to *where* position """
    beam.path += where
    beam.x[:] += beam.a * beam.path
    beam.z[:] += beam.c * beam.path

def show_beam_part(beam, idarr):
    """ Shows photons within an array of ids """
    xx = beam.x[idarr]
    zz = beam.z[idarr]
    plt.scatter(xx, zz)
    plt.show()

def show_beam(beam):
    """ Shows a reasonable part of the beam """
    # Just take first 2000 photons and plot.scatter them
    limit = 2000 if beam.x.size > 2000 else beam.x.size
    rng = range(limit)
    xx = beam.x[rng]
    zz = beam.z[rng]
    plt.scatter(xx, zz)
    plt.show()

def copy_by_index(beam, indarr):
    """ Copies a part of beam """
    outbeam = rs.Beam()
    outbeam.state = beam.state[indarr]
    outbeam.x = beam.x[indarr]
    outbeam.y = beam.y[indarr]
    outbeam.z = beam.z[indarr]
    outbeam.a = beam.a[indarr]
    outbeam.b = beam.b[indarr]
    outbeam.c = beam.c[indarr]
    outbeam.path = beam.path[indarr]
    outbeam.E = beam.E[indarr]
    outbeam.Jss = beam.Jss[indarr]
    outbeam.Jpp = beam.Jpp[indarr]
    outbeam.Jsp = beam.Jsp[indarr]
    if hasattr(beam, 'nRefl'):
        outbeam.nRefl = beam.nRefl[indarr]
    if hasattr(beam, 'elevationD'):
        outbeam.elevationD = beam.elevationD[indarr]
        outbeam.elevationX = beam.elevationX[indarr]
        outbeam.elevationY = beam.elevationY[indarr]
        outbeam.elevationZ = beam.elevationZ[indarr]
    if hasattr(beam, 's'):
        outbeam.s = beam.s[indarr]
    if hasattr(beam, 'phi'):
        outbeam.phi = beam.phi[indarr]
    if hasattr(beam, 'r'):
        outbeam.r = beam.r[indarr]
    if hasattr(beam, 'theta'):
        outbeam.theta = beam.theta[indarr]
    if hasattr(beam, 'order'):
        outbeam.order = beam.order[indarr]
    if hasattr(beam, 'Es'):
        outbeam.Es = beam.Es[indarr]
        outbeam.Ep = beam.Ep[indarr]

    return outbeam

def save_beam(beam, filename = 'global_total.beam'):
    """ OBSOLETE Simply pickle the beam """
    file = open(filename, 'wb')
    pickle.dump(beam, file)
    file.close()

def save_beam_compressed(beam, filename = 'global_total.beam'):
    """ Add letter c at the end of filename to indicate compression """
    file = gzip.open(filename, 'wb')
    pickle.dump(beam, file)
    file.close()

def load_beam(filename):
    """ Load simply pickled beam """
    file = open(filename, 'rb')
    beam = pickle.load(file)
    file.close()

    return beam

def load_beam_compressed(filename):
    """ Load compressed beam """
    file = gzip.open(filename, 'rb')
    beam = pickle.load(file)
    file.close()

    return beam
