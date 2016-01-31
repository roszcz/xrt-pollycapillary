import xrt.backends.raycing.sources as rs
import xrt.runner as xrtr
import xrt.backends.raycing.screens as rsc
import xrt.plotter as xrtp
import xrt.backends.raycing.run as rr
import xrt.backends.raycing as raycing

class BeamPlotter(object):
    """ Simple class for showing the beam with the xrt style plot """
    def __init__(self, beam, pos):
        """ Init """
        self.beam = beam
        self.position = pos
        self.plots = []
        self.beamLine = raycing.BeamLine()
        self.beamLine.screen = rsc.Screen(self.beamLine,
                                          'TheScreen',
                                          (0, pos, 0))
        self.make_run_process()
        self.make_plot()
        self.run_it()

    def make_run_process(self):
        """ ___ """
        def local_process(beamLine, shineOnly1stSource=False):
            photons = self.beam
            screened = beamLine.screen.expose(photons)
            out_dict = {'Screen' : screened}

            return out_dict

        rr.run_process = local_process

    def make_plot(self):
        """ Prepare the only plot """
        bins = 256
        plot = xrtp.XYCPlot(
            # Using named parameters might be good here TODO
            'Screen', (1, 3,),
            beamState='Screen',
            # This is still inside plot
            xaxis=xrtp.XYCAxis(r'$x$', 'mm',
                               bins=bins,
                               ppb=2,
                               limits=None),
            # As is this
            yaxis=xrtp.XYCAxis(r'$z$', 'mm',
                               bins=bins,
                               ppb=2,
                               limits=None),
            # Colorbar and sidebar histogram
            caxis=xrtp.XYCAxis('Energy',
                               '[eV]',
                               data=raycing.get_energy,
                               bins=bins,
                               ppb=2,
                               limits=None)
            ) # plot ends here
        plot.title = "Plot"

        self.plots.append(plot)

    def run_it(self):
        """ Runs """
        xrtr.run_ray_tracing(self.plots,\
                             repeats = 1,\
                             beamLine = self.beamLine,\
                             processes = 1)

