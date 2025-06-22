import numpy             as np
import matplotlib.pyplot as plt

# metpy
import metpy.calc as mpcalc
from metpy.plots import add_metpy_logo, SkewT, Hodograph
from metpy.units import units

class SKEWTPLOT():

    def __init__(self, var):
        self.h = var.H; self.p = var.P; self.T = var.T;   self.Td = var.Td; self.rh = var.RH
        self.U = var.U; self.V = var.V; self.ws = var.ws; self.wd = var.wd

    def plot_skewT(self, CAPE_SHADING_ON=True, HOTOGRAGH_ON=False):
        T = self.T[0:-1] * units.degC;  Td = self.Td[0:-1] * units.degC
        u = self.U[0:-1] * units('m/s'); v = self.V[0:-1] * units('m/s')
        p = self.p[0:-1] * units.hPa

        fig = plt.figure(figsize=(9, 9))
        skew = SkewT(fig, rotation=45)

        skew.plot(p, T, 'r')
        skew.plot(p, Td, 'g')
        skew.plot_barbs(p[::30], u[::30], v[::30])
        skew.ax.set_ylim(1000, 100)
        skew.ax.set_xlim(-10, 40)

        # Set some better labels than the default
        skew.ax.set_xlabel(f'Temperature ({T.units:~P})')
        skew.ax.set_ylabel(f'Pressure ({p.units:~P})')

        # An example of a slanted line at constant T -- in this case the 0
        # isotherm
        skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

        # Add the relevant special lines
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()

        if CAPE_SHADING_ON:
            # Calculate full parcel profile and add to plot as black line
            prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
            skew.plot(p, prof, 'k', linewidth=2)

            # Shade areas of CAPE and CIN
            skew.shade_cin(p, T, prof, Td)
            skew.shade_cape(p, T, prof)

        if HOTOGRAGH_ON:
            self.plot_hotogragh()

        # plt.savefig("/mnt/e/workspace/pic/20220629/skewTwithwindrose.png", dpi=300)
        plt.show()

    def plot_hotogragh(self, target_heights=[10, 2000, 3000, 5000]):

        target_heights = np.array(target_heights)
        indices = np.array([np.abs(self.h - height).argmin() for height in target_heights])
        u_selected = self.U[indices]
        v_selected = self.V[indices]
        h_selected = self.h[indices] 

        ax = plt.axes((0.53, 0.66, 0.2, 0.2))

        h = Hodograph(ax, component_range=6.)
        h.add_grid(increment=2)
        h.plot(u_selected, v_selected)
        h.ax.set_box_aspect(1)
        h.ax.set_yticklabels([])
        h.ax.set_xticklabels([])
        h.ax.set_xticks([])
        h.ax.set_yticks([])
        h.ax.set_xlabel('m/s')
        h.ax.set_ylabel('m/s')

        plt.xticks(np.arange(0, 0, 1))
        plt.yticks(np.arange(0, 0, 1))
        for i in range(0, 6, 2):
            h.ax.annotate(str(i), (i, 0), xytext=(0, 2), textcoords='offset pixels',
                        clip_on=True, fontsize=10, weight='bold', alpha=0.3, zorder=0)
        for i in range(0, 6, 2):
            h.ax.annotate(str(i), (0, i), xytext=(0, 2), textcoords='offset pixels',
                        clip_on=True, fontsize=10, weight='bold', alpha=0.3, zorder=0)

