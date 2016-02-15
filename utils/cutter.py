import numpy as np
from utils import beam as ub
from utils import plotter as up

def cut_wire(beam):
    """ Simulated a rectangular object blocking the beam """
    ids = ((beam.x > -0.2) & (beam.x < -0.17)) |\
	  ((beam.x > -0.1) & (beam.x < -0.07)) |\
	  ((beam.x >  0.0) & (beam.x <  0.03)) |\
	  ((beam.x >  0.1) & (beam.x <  0.13)) |\
	  ((beam.x >  0.2) & (beam.x <  0.23))

    print ids.sum()
    ids = ids != True
    print ids.sum()

    return ids

def make_wires(beam):
    """ Usage example """
    ids = cut_wire(beam)

    ceam = ub.copy_by_index(beam, ids)

    return ceam

