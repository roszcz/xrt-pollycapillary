import numpy as np
from matplotlib import path as mp
from utils import beam as ub
from utils import plotter as up

def cut_slits(beam):
    """ Simulate multiple slits in the way of rays """
    ids = ((beam.x > -0.2) & (beam.x < -0.17)) |\
	  ((beam.x > -0.1) & (beam.x < -0.07)) |\
	  ((beam.x >  0.0) & (beam.x <  0.03)) |\
	  ((beam.x >  0.1) & (beam.x <  0.13)) |\
	  ((beam.x >  0.2) & (beam.x <  0.23))

    return ids

def cut_wires(beam):
    """ Simulated a rectangular objects blocking the beam """

    # Wires are anti-slits
    slit_ids = cut_slits(beam)
    ids = slit_ids != True

    return ids

def make_wires(beam):
    """ Usage example """
    ids = cut_wires(beam)

    ceam = ub.copy_by_index(beam, ids)

    return ceam

def cut_triangle(beam):
    """ Or any other irregular shape using matplotlib.path """
    triangle = mp.Path([(0,0), (0.08, 0.02), (-0.03, 0.02)])

    # Change 2 lists of coordinates into a list of paired coordinates
    points = zip(beam.x, beam.z)
    ids = triangle.contains_points(points)

    ceam = ub.copy_by_index(beam, ids)

    return ceam

