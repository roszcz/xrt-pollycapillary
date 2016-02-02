import xrt.backends.raycing.sources as rs
import xrt.runner as xrtr
import xrt.backends.raycing.screens as rsc
import xrt.plotter as xrtp
import xrt.backends.raycing.run as rr
import xrt.backends.raycing as raycing

class BeamPlotter(object):
    """ Simple class for showing the beam with the xrt style plot """
    def __init__(self, beam):
        """ Init """
        self.beam = beam
        self.position = 1000
        self.x_limit = self.z_limit = None

    def make_run_process(self):
        """ ___ """
        def local_process(beamLine, shineOnly1stSource=False):
            photons = self.beam
            screened = beamLine.screen.expose(photons)
            out_dict = {'Screen' : screened}

            return out_dict

        rr.run_process = local_process

    def show(self, position):
        """ Shows beam in xrt style at the y = position """
        self.position = position
        self.beamLine = raycing.BeamLine()
        self.beamLine.screen = rsc.Screen(self.beamLine,
                                          'TheScreen',
                                          (0, self.position, 0))
        self.make_run_process()
        self.make_plot()
        self.run_it()

    def set_limits(self, xl, zl = None):
        """ If one value is provided it's used for both directions """
        if zl is None:
            zl = xl
        self.x_limit = xl
        self.z_limit = zl

    def make_plot(self):
        """ Prepare the only plot """
        self.plots = []
        bins = 256
        plot = xrtp.XYCPlot(
            # Using named parameters might be good here TODO
            'Screen', (1, 3,),
            beamState='Screen',
            # This is still inside plot
            xaxis=xrtp.XYCAxis(r'$x$', 'mm',
                               bins=bins,
                               ppb=2,
                               limits=self.x_limit),
            # Actually it is z-axis!
            yaxis=xrtp.XYCAxis(r'$z$', 'mm',
                               bins=bins,
                               ppb=2,
                               limits=self.z_limit),
            # Colorbar and sidebar histogram
            caxis=xrtp.XYCAxis('Reflections',
                               'number',
                               # TODO wrap this into a settable member!
                               data=raycing.get_reflection_number,
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

