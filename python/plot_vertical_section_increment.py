import xarray as xr
import numpy as np
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import time

import read_grid_xr
import cplot

ddir='/fs/site6/eccc/mrd/rpndat/ses002/ODA/midas/'
file=ddir+'2022061500_000_inc_0001.nc'
fil0=ddir+'2022061500_000_inc_0000.nc'

INC=xr.open_dataset(file)
IN0=xr.open_dataset(fil0)

Tinc=np.squeeze(INC['bckint'])

lat = read_grid_xr.read_mesh_var(var='nav_lat')
lon = read_grid_xr.read_mesh_var(var='nav_lon')
lev = read_grid_xr.read_mesh_var(var='nav_lev')
mask = np.squeeze(read_grid_xr.read_mesh_var(var='tmask'))

nz=49
Tinc_grid = []

for iz in range(nz):
    print(iz)
    time0 = time.time()
    mask_lon, mask_lat, Tinc_msk = cplot.mask_field(lon.data, lat.data, Tinc[iz].data, mask[iz].data)
    grid_lon, grid_lat, Tinc_giz = cplot.grdfld(mask_lon, mask_lat, Tinc_msk, ddeg=0.25)
    Tinc_grid.append(Tinc_giz)
    print(iz, time.time() - time0)

Tinc_3dgrid=np.stack(Tinc_grid)
     
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.dates as mdates
import matplotlib.cm as cm
import copy

#fig, axe = plt.subplots()
#plt.pcolormesh(grid_lon[:,360], -1.0*lev[:-1], Tinc_3dgrid[:, :, 360], cmap=cmap_anom, contours=)
#fig.savefig('EqnInc.png')

pcolormesh(grid_lon[:,360], -1.0*lev[IZ], Tinc_3dgrid[IZ[0], :, 360], levels=np.arange(-4.5, 5.0, 1), cmap=cmap_anom, outfile='EqnInc.png')
pcolormesh(grid_lon[:,440], -1.0*lev[IZ], Tinc_3dgrid[IZ[0], :, 360], levels=np.arange(-4.5, 5.0, 1), cmap=cmap_anom, outfile='N20.png')
pcolormesh(grid_lon[:,520], -1.0*lev[IZ], Tinc_3dgrid[IZ[0], :, 360], levels=np.arange(-4.5, 5.0, 1), cmap=cmap_anom, outfile='N40.png')

dmap = 'seismic'
def pcolormesh(x, y, field, levels=None, ticks=None, cmap=dmap, outfile='plt.png', 
               title='', suptitle=None,
               cbar=True, obar='vertical', fontsizes=None, marks=None, add_gridlines=False, **kwargs):
    fig, ax = plt.subplots()
    if ( isinstance(levels, type(None) ) ):
        norm=None
    else:
        Ncolors=plt.get_cmap(cmap).N
        norm = clr.BoundaryNorm(levels, ncolors=Ncolors, clip=False, extend='both')
    if ( isinstance(norm, type(None) ) ):
        mesh = ax.pcolormesh(x, y, field, cmap=cmap)
    else:
        mesh = ax.pcolormesh(x, y, field, norm=norm, cmap=cmap)
    if ( cbar ): 
        #print('cbar', cbar_fontsize)
        cbar_fig=fig.colorbar(mesh, format='%.3f',orientation=obar, ticks=ticks)
        #cbar_fig.ax.tick_params(labelsize=cbar_fontsize)
        #cbar_fig.set_label(label=cbar_label[0], size=cbar_label[1], weight=cbar_label[2])
    if add_gridlines:
        gl = ax.gridlines(linewidth=1, color='darkmagenta', alpha=0.75, linestyle='--', draw_labels=True)
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.ylabels_right=True
        gl.xlines = True
        #gl.xlocator = mticker.FixedLocator(lonloc)
        #gl.ylocator = mticker.FixedLocator(latloc)
        #gl.xformatter = LONGITUDE_FORMATTER
        #gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'color': 'black', 'weight': 'bold', 'fontsize': 14}
        gl.ylabel_style = {'color': 'black', 'weight': 'bold', 'fontsize': 14}
    #print('title', title_fontsize)
    if ( suptitle != None ): fig.suptitle(suptitle, fontsize=14)
    ax.set_title(title, fontsize=14)
    if ( isinstance(outfile, str) ):  outfile_list = [ outfile ]
    if ( isinstance(outfile, list) ): outfile_list = outfile
    for ofile in outfile_list:
        fig.savefig(ofile,bbox_inches='tight')
    plt.close(fig)
    return
 
