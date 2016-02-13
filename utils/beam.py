import pickle
import gzip
from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xrt.backends.raycing.sources as rs

def get_beam_part(beam, hitpoint, radius):
    """ Copies a square part of beam hitting the point around radius """
    x, z = hitpoint
    ids = (beam.x < x + radius) &\
          (beam.x > x - radius) &\
          (beam.z < z + radius) &\
          (beam.z > z - radius)
    out = copy_by_index(beam, ids)

    return out

# FIXME this name is highly misleading
def move_beam_to(beam, where_to):
    """ Propagates the beam in vacuum """
    beam.y[:] = beam.y[:] - where_to

    xx = 1., 0., 0.
    zz = 0., 0., 1.
    yy = np.cross(zz, xx)

    xyz = beam.x, beam.y, beam.z
    beam.x[:], beam.y[:], beam.z[:] = \
	    sum(c*b for c, b in zip(xx, xyz)),\
	    sum(c*b for c, b in zip(yy, xyz)),\
	    sum(c*b for c, b in zip(zz, xyz))
    abc = beam.a, beam.b, beam.c
    beam.a[:], beam.b[:], beam.c[:] = \
	    sum(c*b for c, b in zip(xx, abc)),\
	    sum(c*b for c, b in zip(yy, abc)),\
	    sum(c*b for c, b in zip(zz, abc))

    path = -beam.y / beam.b
    beam.path += path

    beam.x[:] += beam.a * path
    beam.z[:] += beam.c * path
    beam.y[:] = where_to

def frame_to_beam(frame):
    """ pd.DataFrame to xrt.Beam converter """
    beam = rs.Beam()
    # Convert
    beam.state = frame.state.values
    beam.x = frame.x.values
    beam.y = frame.y.values
    beam.z = frame.z.values
    beam.a = frame.a.values
    beam.b = frame.b.values
    beam.c = frame.c.values
    beam.path = frame.path.values
    beam.E = frame.E.values
    beam.Jss = frame.Jss.values
    beam.Jpp = frame.Jpp.values
    beam.Jsp = frame.Jsp.values

    if 'nRefl' in frame:
        beam.nRefl = frame.nRefl.values

    return beam

def beam_from_csvs(folder):
    """ Create beam from multiple csv files inside one folder """
    files = glob(folder + '/*csv')
    frames = []
    for file in files:
        frames.append(pd.DataFrame.from_csv(file))

    # Create beam from multiple pd.DataFrames
    beam = frame_to_beam(pd.concat(frames))

    # FIXME remove photons with too many reflections
    # since they are obviously ill, investigate why is so pls
    ids = beam.nRefl < beam.nRefl.max()

    # Keep only good photons
    ceam = copy_by_index(beam, ids)
    return ceam

def make_dataframe(beam):
    """ Conver beam to a pd.DataFrame object """
    # Create a dictionary with {column : series}
    data = {'state'     : pd.Series(beam.state),
            'x'         : pd.Series(beam.x),
            'y'         : pd.Series(beam.y),
            'z'         : pd.Series(beam.z),
            'a'         : pd.Series(beam.a),
            'b'         : pd.Series(beam.b),
            'c'         : pd.Series(beam.c),
            'path'      : pd.Series(beam.path),
            'E'         : pd.Series(beam.E),
            'Jss'       : pd.Series(beam.Jss),
            'Jpp'       : pd.Series(beam.Jpp),
            'Jsp'       : pd.Series(beam.Jsp)
            }
    # Update with columns that nod necessary exiest in a beam
    if hasattr(beam, 'nRefl'):
        data.update({'nRefl' : beam.nRefl})

    frame = pd.DataFrame(data)
    return frame

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

def plot_beam(beam, pos):
    """ Prepares xrt-style histogram generated on Screen at *pos* """
    pass

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

def save_beam_compressed(beam, filename = 'global_total.beamc'):
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
