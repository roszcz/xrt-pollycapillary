import numpy as np
from matplotlib import path as mp
from utils import beam as ub
from utils import plotter as up

def cut_slits(beam, shift = 0):
    """ Simulate multiple slits in the way of rays """
    ids = ((beam.x > -0.2 + shift) & (beam.x < -0.17 + shift)) |\
	  ((beam.x > -0.1 + shift) & (beam.x < -0.07 + shift)) |\
	  ((beam.x >  0.0 + shift) & (beam.x <  0.03 + shift)) |\
	  ((beam.x >  0.1 + shift) & (beam.x <  0.13 + shift)) |\
	  ((beam.x >  0.2 + shift) & (beam.x <  0.23 + shift))

    return ids

def cut_wires(beam, shift = 0):
    """ Simulated a rectangular objects blocking the beam """

    # Wires are anti-slits
    slit_ids = cut_slits(beam, shift)
    ids = slit_ids != True

    return ids

def make_wires(beam, shift = 0):
    """ Usage example """
    ids = cut_wires(beam, shift)

    ceam = ub.copy_by_index(beam, ids)

    return ceam

def cut_triangle(beam):
    """ Or any other irregular shape using matplotlib.path """
    triangle = mp.Path([(-0.04, -0.02), (0.08, 0.02), (-0.06, 0.02)])

    # Change 2 lists of coordinates into a list of paired coordinates
    points = zip(beam.x, beam.z)
    ids = triangle.contains_points(points)

    ceam = ub.copy_by_index(beam, ids)

    return ceam

def cut_left_half(beam):
    """ why not """
    ids = beam.x <= 0

    ceam = ub.copy_by_index(beam, ids)

    return ceam
