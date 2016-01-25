import numpy as np
import matplotlib.pyplot as plt

"""
Here we are calculating polynomial coefficients describing
bent shape of a single capillary inside a Lens with
provided parameters
"""

# TODO Make a picture explaining those
def capillary_curvature(x,y,D):
    """ Calculates capillary curvature for distance x from
    the center and other lens properties described in y and D """
    y0 = y['y0']
    y1 = y['y1']
    ym = y['ym']
    y2 = y['y2']
    yf = y['yf']
    h1 = x
    Din     = D['Din']
    Dout    = D['Dout']
    Dmax    = D['Dmax']
    h2 = h1 * Dout/Din
    hm = 0.5*Dmax * h1/(Din/2.)
    # y(x) = p0 + p1 x + p2 x**2 + p3 x**3 + p4 x**4 + p5 x**5
    a = []
    b = []
    # Preparing A*p = B matrices for linalg.solve 
    # y(y1) == h1
    a.append(shape_coeffs(y1))
    b.append(h1)
    # y(y2) == h2
    a.append(shape_coeffs(y2))
    b.append(h2)
    # y(ym) == hm
    a.append(shape_coeffs(ym))
    b.append(hm)
    # y'(y1) == S1'(y1)
    # first find left slope
    s1 = h1/(y1-y0)
    a.append(diff_coeffs(y1))
    b.append(s1)
    # y'(y2) == S2'(x)
    s2 = -h2/(yf-y2)
    a.append(diff_coeffs(y2))
    b.append(s2)
    # y'(ym) == 0
    a.append(diff_coeffs(ym))
    b.append(0.)
    p = np.linalg.solve(a,b)
    return p

def shape_coeffs(x):
    """ This method is poorly named """
    coeff_array = [1., x, x**2, x**3, x**4, x**5]
    return coeff_array

def diff_coeffs(x):
    """ as is this """
    coeff_array = [0., 1., 2*x, 3*x**2, 4*x**3, 5*x**4]
    return coeff_array

def radius_curvature(y, r):
    """ Use this to get polynomial coefficients for
    position dependant capillary radius """
    B = [r['rIn'], r['rOut'], r['rMax'] ]
    A = []
    y1 = y['y1']
    A.append([1., y1, y1**2])
    y2 = y['y2']
    A.append([1., y2, y2**2])
    ym = y['ym']
    A.append([1., ym, ym**2])

    return np.linalg.solve(A,B)

if __name__ == '__main__':
    """ python lenses/bendshapes.py """
    # y-parameters of a capillary
    y = {'y0' : 0., 'y1' : 40., 'ym' : 85, 'y2' : 140, 'yf' : 155}

    # D-parameters of the lens
    D = {'Din' : 4.5, 'Dout' : 2.4, 'Dmax' : 8.0}

    # Entrance distance from the center
    x_in = -1.1

    # Calculate 5th degree polynomial describing capillary shape
    p = capillary_curvature(x_in,y,D)

    # Show 
    # FIXME just ugly
    x = np.linspace(y['y1'],y['y2'],1000)
    yfin = p[0] + p[1]*x + p[2]*x**2 + p[3]*x**3 + p[4]*x**4 + p[5]*x**5
    fig1 = plt.figure(1,figsize=(10,4))
    ax1 = plt.subplot(111, label='capillary')
    ax1.set_xlim([y['y0'],y['yf']])
    ax1.set_ylim([-4, 4])
    ax1.plot(x,yfin,'r-', lw=2)
    ax1.plot([y['y0'],y['y1']],[0,x_in],'k-',lw=0.5)
    x2 = x_in * D['Dout'] / D['Din']
    ax1.plot([y['y2'], y['yf']],[x2,0],'k-',lw=0.5)
    plt.show()
