import xrt.backends.raycing.sources as rs
import xrt.backends.raycing as raycing

class FitGeometricSource(rs.GeometricSource):
    """ Special source generating photons exactly at the
    capillary entrance """
    def __init__(self, *args, **kwargs):
        rs.GeometricSource.__init__(self, *args, **kwargs)

def test_it():
    """ Check if compiles """
    # Source parameters
    nrays       = 1000
    distE       = 'normal'
    energies    = (9000, 100)
    # x-direction
    distx       = 'flat'
    dx          = 1
    distxprime  = 'flat'
    dxprime     = 1
    # z-direction
    distz       = 'flat'
    dz          = 1
    distzprime  = 'flat'
    dzprime     = 1

    beamLine = raycing.BeamLine()
    src = FitGeometricSource(
            beamLine,'source',(0,0,0), nrays=nrays,
            distx=distx, dx=dx, distxprime=distxprime, dxprime=dxprime,
            distz=distz, dz=dz, distzprime=distzprime, dzprime=dzprime,
            distE=distE, energies=energies,
            polarization=None)

    return src
