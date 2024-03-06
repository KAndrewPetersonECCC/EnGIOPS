import numpy as np
import numbers
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import shapely.geometry as sgeometry

import matplotlib as mpl

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import cartopy.crs as ccrs

import sys
this_dir='/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python'
sys.path.insert(0, this_dir)
import cplot
import fft_giops
import fourier_analysis

GDX=1000; gdx=10.0
LLGRID, BOX1 =  fft_giops.create_box( (0, 0), size=1000, dx=gdx, theta=0.0 )
LLGRID, BOX2 =  fft_giops.create_box( (-60, 45), size=GDX, dx=gdx, theta=0.0 )
LLGRID, BOX3 =  fft_giops.create_box( ( 60, -45), size=GDX, dx=gdx, theta=0.0 )
LLGRID, BOX4 =  fft_giops.create_box( ( 160, 10), size=GDX, dx=gdx, theta=0.0 )
ROXES = [BOX1, BOX2, BOX3, BOX4]

BOX1 = [(0, -5), (30, -5), (30, 5), (0, 5), (0, -5)]
BOX2 = [(-180, -45), (-140, -45), (-140, -55), (-180, -55), (-180, -45)]
BOX3 = [(170, 45), (-170, 45), (-170, 55), (170, 55), (170, 45)]
BOX4 = [(-20, 50), (20, 50), (20, 70), (-20, 70), (-20, 50)]
SOXES = [BOX1, BOX2, BOX3, BOX4]
projections, pcarree = cplot.make_projections()

def create_BOXES():
    BOXES, GRIDS, LATS = fourier_analysis.create_BOXES()
    return BOXES, GRIDS, LATS

def tile_patches(BOXES, COLORS, cmap='seismic', project='PlateCarree', outfile='tile.png'):
    patches = []
    for ibox, BOX in enumerate(BOXES):
        polygon = mpatches.Polygon(BOX)
        patches.append(polygon)

    fig = plt.figure()
    ax = plt.subplot(projection=projections[project])
    plt.set_cmap(cmap)

    p = PatchCollection(patches, alpha=0.4)
    p.set_array(COLORS)
    ax.add_collection(p)
    ax.set_global()
    ax.coastlines()
    fig.colorbar(p, ax=ax, orientation='horizontal')

    fig.savefig(outfile)
    plt.close(fig)

def simple_test(BOXES, project='PlateCarree'):
    ax = plt.subplot(projection=projections[project])
    ax.coastlines()

    colors=['r','b','m', 'g']
    for ii,artist in enumerate(patches):
      artist.set(color=colors[ii])
      ax.add_artist(artist)

    
    fig.savpefig('tile.png')
    plt.close(fig)
    return

def cplot_tiles(BOXES, COLORS, SCALE=None, cmap='seismic', project='PlateCarree', outfile='tile.png', ticks=None):
    if ( isinstance(SCALE, type(None)) ):
       smin = 0
       smax = max(COLORS)
    elif ( isinstance(SCALE, numbers.Number) ):
      smin=0
      smax=SCALE
    else: 
      smin = SCALE[0]
      smax = SCALE[1]
    fig = plt.figure()
    ax = plt.subplot(projection=ccrs.PlateCarree())
    plt.set_cmap(cmap)
    colormap = mpl.cm.get_cmap()
    norm = mpl.colors.Normalize(vmin=smin, vmax=smax)
    for ibox, BOX in enumerate(BOXES):
        polygon = sgeometry.Polygon(BOX)
        rgba=colormap(norm(COLORS[ibox]))
        ax.add_geometries([polygon], crs=ccrs.PlateCarree().as_geodetic(), fc=rgba, ec="red", alpha=0.65)

    sm = mpl.cm.ScalarMappable(cmap=colormap)
    #sm._A = COLORS
    sm.set_clim(vmin=smin, vmax=smax)
    #print('colorbar', smin, smax, sm._A)
    cb = fig.colorbar(sm, ax=ax, orientation='horizontal')
    if ( not isinstance(ticks, type(None)) ):
        cb.set_ticks(ticks)
    ax.coastlines()
    fig.savefig(outfile,bbox_inches='tight')
    plt.close(fig)

    return

def test():
    BOXES, GRIDS, LATS = create_BOXES()
    COLORS = 100 * np.random.rand(len(BOXES))
    tile_patches(BOXES, COLORS, cmap='seismic', project='PlateCarree', outfile='pile.png')
    cplot_tiles(BOXES, COLORS, SCALE=100, cmap='seismic', project='PlateCarree', outfile='tile.png')
    return
