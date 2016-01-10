import pickle
import gzip

def save_beam(beam, filename = 'global_total.beam'):
    """ Simply pickle the beam """
    file = open(filename, 'wb')
    pickle.dump(beam, file)
    file.close()

def save_beam_compressed(beam, filename = 'global_total.beam'):
    """ Add letter c at the end of filename to indicate compression """
    filename += 'c'
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
