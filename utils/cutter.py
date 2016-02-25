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

def outside_circle(beam, position = [0, 0], radius = 0.05):
    """ Get indexes of rays not hitting this circle """
    N_ = 100
    s = [position[0] + radius * np.sin(2*np.pi*th/N_) for th in range(N_)]
    c = [position[1] + radius * np.cos(2*np.pi*th/N_) for th in range(N_)]

    circ = mp.Path(zip(s,c))

    ids = circ.contains_points(zip(beam.x, beam.z))

    print 'Inside:', ids.sum()
    # Go outside
    ids = ids == False

    print 'Out:', ids.sum()

    return ids

def cut_circle(beam, position = [0, 0], radius = 0.01):
    """ Pinholes are circular! """
    N_ = 100
    s = [position[0] + radius * np.sin(2*np.pi*th/N_) for th in range(N_)]
    c = [position[1] + radius * np.cos(2*np.pi*th/N_) for th in range(N_)]

    circ = mp.Path(zip(s,c))

    ids = circ.contains_points(zip(beam.x, beam.z))

    ceam = ub.copy_by_index(beam, ids)

    return ceam

def create_defects(beam, howmany):
    """ Try to simulate defect related imaging """
    # Container for single-defect ids
    dids = []

    # Define defect radius
    d_rad = 0.01

    for it in range(howmany):
	# Generate random positions from [-2 :: 2]
	rx = (-0.5 + np.random.random()) * 4.0
	ry = (-0.5 + np.random.random()) * 4.0
	pos = [rx, ry]

	print 'Creating defect at:', pos, 'With radius:', d_rad

	dids.append(outside_circle(beam, pos, d_rad))

    # Get final set of good rays
    fids = np.ones_like(dids[0])
    # Array of truth
    fids = fids < 2

    for ids in dids:
	fids &= ids

    ceam = ub.copy_by_index(beam, fids)

    return ceam
