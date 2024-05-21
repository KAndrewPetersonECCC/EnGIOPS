import sys
import numpy as np
import datetime
import pytz
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
#mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import cartopy.crs as ccrs

sys.path.insert(0, '/home/dpe000/python/utm-0.7.0')
import utm

hdir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
hdir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mdir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
mdir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

import scipy.interpolate
import scipy.stats
import scipy.signal
import scipy.fft as spyfft
import matplotlib.pyplot as plt

addpath='/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/CIOPS/analysis/Ensemble_CIOPS_analysis/python'
sys.path.insert(0, addpath)

import stfd
import cplot
import write_nc_grid

utc=pytz.timezone('UTC')
epoch=datetime.datetime(1970,1,1,0,0,0,0,utc)

def seconds_since_epoch( date, epoch=epoch):
    seconds = ( date - epoch ).total_seconds()
    return seconds

dmap='gist_stern'
dmap='gist_stern_r'

mdir3='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_hub/'
mdir4='/fs/site4/eccc/mrd/rpnenv/dpe000/maestro_hub/'

def dlon_in_km(dx, lat, inverse=False):
    olon = 111.111 * np.cos(np.pi * lat / 180.0)
    dlon = dx / olon
    if ( inverse ):
        dlon = dx * olon  # where dx is a dlon and dlon a dx.
    return dlon

def lat_line(lat, lon0, dx, DX):
    Nlon = int(DX/dx)
    dlon = dlon_in_km(dx, lat)
    Dlon = dlon_in_km(DX, lat)
    lons = lon0 + dlon * np.arange(Nlon+1)
    lats = np.array([ lat for loni in lons ])
    PTS = [ [loni, lat] for loni in lons ]
    return lons, lats, PTS
    
def lon_line(lon, lat0, dy, DY):
    Nlat = int(DY/dy)
    dlat = dlon_in_km(dy, 0) # separation of lines of longitude can be approx. by separation of lines of latitude at equator (spherical earth). 
    lats = lat0 + dlat * np.arange(Nlat+1)
    lons = np.array([ lon for lati in lats ])
    PTS = [ [lon, lati] for lati in lats]
    return lons, lats, PTS
    
def create_box( latlon_SW_corner, size=1000.0, dx=5.0, theta=0.0 ):
    size_m = size * 1000.
    dx_m = dx * 1000.
    (lon_SW_corner, lat_SW_corner) = latlon_SW_corner
    #
    # Create box at arbitrary location and angle
    (X_array, Y_array), xy_box = make_grid_box( (0.0, 0.0), size_m, dx_m )
    # Create a grid
    (Y_grid, X_grid) = np.meshgrid(Y_array, X_array)
    #print(grid_box_corners((X_grid, Y_grid)))
    #
    # Get box coordinates in axes parallel to local North/East cartesian coordinate system
    # Negative theta, as theta as going from rotated grid to non-rotated grid.
    (X_EWcoor,Y_NScoor) = rotate_by_theta((X_grid, Y_grid), -1.0*theta)
    # Find the origin of the box (SW corner) in the UTM coordinate system
    (X_corner, Y_corner, zone, name) = utm.from_latlon(lat_SW_corner, lon_SW_corner)
    # Translate the Eastward and Northward coordinates to UTM coordinates.
    (X_UTM, Y_UTM) = translate_grid( (X_EWcoor, Y_NScoor), (X_corner, Y_corner) )
    #print(grid_box_corners((X_UTM, Y_UTM)))
    # Convert to Lat/Lon
    lat_grid, lon_grid = utm.to_latlon(X_UTM, Y_UTM, zone, name, strict=False)
    LLGRID=(lon_grid, lat_grid)
    # Find corners of lat/lon grid
    BOX = grid_box_corners(LLGRID)
    #prin(BOX)
    #print(map_box(grid_box_corners((X_UTM, Y_UTM)), zone, name))
    return LLGRID, BOX

def create_rectangle( latlon_SW_corner, size_x=1000.0, size_y=1000.0, dx=5.0, dy=5.0, theta=0.0 ):
    size_mx = size_x * 1000.
    size_my = size_y * 1000.0
    dx_m = dx * 1000.
    dy_m = dy * 1000.0
    (lon_SW_corner, lat_SW_corner) = latlon_SW_corner
    #
    # Create box at arbitrary location and angle
    (X_array, Y_array), xy_box = make_grid_rect( (0.0, 0.0), size_mx, dx_m, size_my, dy_m)
    # Create a grid
    (Y_grid, X_grid) = np.meshgrid(Y_array, X_array)
    #print(grid_box_corners((X_grid, Y_grid)))
    #
    # Get box coordinates in axes parallel to local North/East cartesian coordinate system
    # Negative theta, as theta as going from rotated grid to non-rotated grid.
    (X_EWcoor,Y_NScoor) = rotate_by_theta((X_grid, Y_grid), -1.0*theta)
    # Find the origin of the box (SW corner) in the UTM coordinate system
    (X_corner, Y_corner, zone, name) = utm.from_latlon(lat_SW_corner, lon_SW_corner)
    # Translate the Eastward and Northward coordinates to UTM coordinates.
    (X_UTM, Y_UTM) = translate_grid( (X_EWcoor, Y_NScoor), (X_corner, Y_corner) )
    print(grid_box_corners((X_UTM, Y_UTM)))
    # Convert to Lat/Lon
    lat_grid, lon_grid = utm.to_latlon(X_UTM, Y_UTM, zone, name, strict=False)
    LLGRID=(lon_grid, lat_grid)
    # Find corners of lat/lon grid
    BOX = grid_box_corners(LLGRID)
    print(BOX)
    print(map_box(grid_box_corners((X_UTM, Y_UTM)), zone, name))
    return LLGRID, BOX

def map_box(xy_box, zone, name):
    LL_box = []
    for xy_cor in xy_box: 
        x_cor, y_cor = xy_cor
        lat_cor, lon_cor = utm.to_latlon(x_cor, y_cor, zone, name, strict=False)
        LL_box.append( (lon_cor, lat_cor) )
    return LL_box
    
def grid_box_corners(LLGRID):
    lon=LLGRID[0]
    lat=LLGRID[1]
    BOX=[]
    for corner in range(5):
        if ( corner == 0 ): i= 0; j= 0
        if ( corner == 1 ): i=-1; j= 0
        if ( corner == 2 ): i=-1; j=-1
        if ( corner == 3 ): i= 0; j=-1
        if ( corner == 4 ): i= 0; j= 0
        corner=( lon[i,j], lat[i,j] )
        BOX.append(corner)
    return BOX

def make_grid_box( corner, length, DX ):
    x_corner = corner[0]
    y_corner = corner[1]
    xy_grid =  np.arange(0, length+DX/2.0, DX) 
    N = len(xy_grid)
    x_grid = x_corner + xy_grid
    y_grid = y_corner + xy_grid
    # X_box = [ Lower left corner, Lower right corner, Upper right corner, Upper Left Corner ]
    xy_box = [ (x_grid[0], y_grid[0]), (x_grid[-1], y_grid[0]), (x_grid[-1], y_grid[-1]), (x_grid[0], y_grid[-1]), (x_grid[0], y_grid[0]) ]
    return (x_grid, y_grid), xy_box
    
def make_grid_rect( corner, length_x, DX, length_y, DY ):
    x_corner = corner[0]
    y_corner = corner[1]
    x_grid =  np.arange(0, length_x+DX/2, DX)
    y_grid =  np.arange(0, length_y+DY/2, DY) 
    Nx = len(x_grid)
    Ny = len(y_grid)
    x_grid = x_corner + x_grid
    y_grid = y_corner + y_grid
    # X_box = [ Lower left corner, Lower right corner, Upper right corner, Upper Left Corner ]
    xy_box = [ (x_grid[0], y_grid[0]), (x_grid[-1], y_grid[0]), (x_grid[-1], y_grid[-1]), (x_grid[0], y_grid[-1]), (x_grid[0], y_grid[0]) ]
    return (x_grid, y_grid), xy_box

def rotate_by_theta(XY, theta):
    #Rotate Cartesian coordinates by theta degrees clockwise.
    X, Y = XY
    
    theta_rads = theta * np.pi / 180.0
    
    x = X * np.cos(theta_rads) - Y * np.sin(theta_rads)
    y = X * np.sin(theta_rads) + Y * np.cos(theta_rads)
    
    return (x, y)

def translate_grid(XY, XY_0):
    #Translate coordinate system by X_0, Y_0
    # X_0, Y_0 is the location of the origin of the X,Y coordinate system in x,y 
    
    X, Y = XY
    X_0, Y_0 = XY_0
    
    x = X + X_0
    y = Y + Y_0
    
    return (x, y)

def draw_box(ax, box, color='b'):
    x_box = [ corner[0] for corner in box ]
    y_box = [ corner[1] for corner in box ]
    ax.plot(x_box, y_box, color=color, linestyle='-', transform=ccrs.Geodetic() )
    return ax
    
def pcolormesh_with_box(lon, lat, field, levels=None, ticks=None, cmap=dmap, project='PlateCarree', 
                        outfile='plt.png', box=[-180, 180, -90, 90], 
                        make_global=False, title='', cbar=True, obar='vertical', 
                        plot_boxes=[], box_colors=['b'], plot_text=[], loco_text=[], **kwargs):

    fig = plt.figure()
    projections, pcarree = cplot.make_projections(**kwargs)
    ax = plt.subplot(projection=projections[project])

    if ( isinstance(levels, type(None) ) ):
        norm=None
    else:
        Ncolors=plt.get_cmap(cmap).N
        norm = clr.BoundaryNorm(levels, ncolors=Ncolors, clip=True)

    if ( make_global ):
        ax.set_global()
    else:
        ax.set_extent(box, crs=ccrs.PlateCarree())
    if ( isinstance(norm, type(None) ) ):
        mesh = ax.pcolormesh(lon, lat, field, cmap=cmap,transform=pcarree)
    else:
        mesh = ax.pcolormesh(lon, lat, field, norm=norm, cmap=cmap,transform=pcarree)
    mesh.set_cmap(cmap)
    if ( cbar ): 
        fig.colorbar(mesh, format='%.2f',orientation=obar, ticks=ticks)
        
    ax.coastlines()

    box_color=box_colors[0]   
    for ibox, plot_box in enumerate(plot_boxes):
        if ( len(box_colors) > ibox ):  box_color=box_colors[ibox]
        draw_box(ax, plot_box, color=box_color)    
    for itext, plot_this in enumerate(plot_text):
        tlon, tlat = loco_text[itext]
        ax.text(tlon, tlat, plot_this, fontsize=10, weight='bold')
    ax.set_title(title)
    fig.savefig(outfile,bbox_inches='tight')
    plt.close(fig)
    return

def interpolate_to_box(FLD, LL_mod, LL_box, method='nearest'):
    lon_mod, lat_mod = LL_mod
    lon_box, lat_box = LL_box
    #
    FLD_box = scipy.interpolate.griddata( (lon_mod.flatten(), lat_mod.flatten()), FLD.flatten(), (lon_box, lat_box), method=method)
    return FLD_box
    
def interpolate_to_box_with_mask(FLD, LL_mod, LL_box, method='nearest', missing=-999):
    lon_mod, lat_mod = LL_mod
    lon_box, lat_box = LL_box
    #
    ISEA = np.where(FLD.mask == False)
    #print(ISEA)
    FLD_SEA = FLD[ISEA]
    lon_sea = lon_mod[ISEA]
    lat_sea = lat_mod[ISEA]
    #print('SHAPES', FLD_SEA.shape, lon_sea.shape, lat_sea.shape, lon_box.shape, lat_box.shape)
    if ( method == '2sweep' ):
        FLD_box = scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_box, lat_box), method='linear', fill_value=missing)
        FLD_rep = scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_box, lat_box), method='nearest' )
        replace = np.where(FLD_box == missing )
        FLD_box[replace] = FLD_rep[replace]
    else:
        FLD_box =  scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_box, lat_box), method=method, fill_value=np.NaN)
    return FLD_box

def interpolate_to_boxes(FLD, LL_mod, LL_BOXES, method='nearest', missing=-999):
    lon_mod, lat_mod = LL_mod
    #
    ISEA = np.where(FLD.mask == False)
    #print(ISEA)
    FLD_SEA = FLD[ISEA]
    lon_sea = lon_mod[ISEA]
    lat_sea = lat_mod[ISEA]

    nb = len(LL_BOXES)
    nx, ny = LL_BOXES[0][0].shape
    for ibox, LL_box in enumerate(LL_BOXES):
        lon_box, lat_box = LL_box
        if ( ibox == 0 ): 
            lon_allbox = lon_box.flatten()
            lat_allbox = lat_box.flatten()
        else:
            lon_allbox = np.concatenate([lon_allbox, lon_box.flatten()])
            lat_allbox = np.concatenate([lat_allbox, lat_box.flatten()])
    
    if ( method == '2sweep' ):
        FLD_allbox = scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_allbox, lat_allbox), method='linear', fill_value=missing)
        FLD_allrep = scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_allbox, lat_allbox), method='nearest' )
        replace = np.where(FLD_allbox == missing )
        FLD_allbox[replace] = FLD_allrep[replace]
    else:
        FLD_allbox =  scipy.interpolate.griddata( (lon_sea, lat_sea), FLD_SEA, (lon_allbox, lat_allbox), method=method, fill_value=np.NaN)
    
    FLD_allbox = np.reshape(FLD_allbox, (nb, nx, ny) )
    FLD_BOXES = []
    for ib in range(nb):
        FLD_BOXES.append(FLD_allbox[ib, :, :])
    return FLD_BOXES

def interpolate_to_boxes_slow(FLD, LL_mod, LL_BOXES, method='nearest', missing=-999):
    FLD_BOXES = []
    for LL_box in LL_BOXES:
        FLD_BOX = interpolate_to_box_with_mask(FLD, LL_mod, LL_box, method=method, missing=missing)
        FLD_BOXES.append(FLD_BOX)
    return FLD_BOXES
        
def get_fft_ps(GRID):
    FFT = np.fft.fft2(GRID, norm='forward')
    PSD = get_psd(FFT)
    return PSD, FFT

def get_cfft_ps(GRID):
    FFT = spyfft.dctn(uu,norm='forward')  # LS/SYED use 'ortho' but then divide by sqrt(N) -- same thing!
    PSD = get_psdr(FFT)
    return  
      
def get_welch_psd(GRID):
    nx, ny = GRID.shape
    kw, psd_x = scipy.signal.welch(GRID, 1, axis=1, window='hann')
    kw, psd_y = scipy.signal.welch(GRID, 1, axis=0, window='hann')
    psd_x = np.mean(psd_x, axis=0)
    psd_y = np.mean(psd_y, axis=1)
    psd = 0.5*(psd_x+psd_y)
    return kw, psd

def get_psd(FFT):
    PSD = np.abs( FFT * np.conj(FFT) )
    return PSD

def get_psdr(FFT):
    PSD = np.abs( FFT * FFT )
    return PSD

def find_wavenumber_norm(N, grid_step):
    wavenumber = np.fft.fftfreq(N, grid_step)
    K2D = np.meshgrid(wavenumber, wavenumber)
    knorm = np.sqrt(K2D[0]**2 +K2D[1]**2)
    return knorm, wavenumber

def find_wavenumber(N, grid_step):
    wavenumber = np.fft.fftfreq(N, grid_step)
    return wavenumber

def setup_Kbins(N, grid_step):
    kbins = np.arange(0.5, N/2., 1.)/(grid_step*N/np.sqrt(2))
    kvals = 0.5 * (kbins[1:] + kbins[:-1])
    return kbins, kvals

def plot_psd(ps, grid_step, output_prefix='./'):
    Nx,Ny = ps.shape
    if ( Nx == Ny ): N=Nx
    #
    knorm = find_wavenumber_norm(N, grid_step)    
    kbins, kvals = setup_Kbins(N, grid_step)
    Abins, _, _ = scipy.stats.binned_statistic(knorm.flatten(), ps.flatten(), statistic = "mean",bins = kbins)
    # Do not normalize until this is all figured out.
    #Abins *= 4. * np.pi / 3. * (kbins[1:]**3 - kbins[:-1]**3)
    #ps_norm = 4.0 * np.pi * np.square(knorm) * dk
    #
    idx = np.argsort(knorm.flatten())
    fig, ax = plt.subplots()
    ax.loglog(knorm.flatten()[idx], ps.flatten()[idx])
    ax.loglog(kvals, Abins)
    ax.set_xlabel("$k$")
    ax.set_ylabel("$P(k)$")
    fig.tight_layout()
    fig.savefig(output_prefix+"PSD_loglog.png", dpi = 300, bbox_inches = "tight")
    plt.close(fig)
    #
    fig, ax = plt.subplots()
    ax.semilogx(knorm.flatten()[idx], ps.flatten()[idx])
    ax.semilogx(kvals, Abins)
    ax.set_xlabel("$k$")
    ax.set_ylabel("$P(k)$")
    fig.tight_layout()
    fig.savefig(output_prefix+"PSD_semilogx.png", dpi = 300, bbox_inches = "tight")
    plt.close(fig)
    #
    return

def plot_psd_multi(ps_list, grid_step, labels=None, output_prefix='./'):

    fig1, ax1 = plt.subplots()
    #fig2, ax2 = plt.subplots()
    colors = ['r','b','g','c','m']
    for ii, ps in enumerate(ps_list):  
        color=colors[ii%5]
        if ( not isinstance(labels, type(None) ) ):
            label=labels[ii]
        else:
            label=''
        Nx,Ny = ps.shape
        if ( Nx == Ny ): N=Nx
        #
        knorm = find_wavenumber_norm(N, grid_step)    
        kbins, kvals = setup_Kbins(N, grid_step)
        Abins, _, _ = scipy.stats.binned_statistic(knorm.flatten(), ps.flatten(), statistic = "mean",bins = kbins)
        # Do not normalize until this is all figured out.
        #Abins *= 4. * np.pi / 3. * (kbins[1:]**3 - kbins[:-1]**3)
        idx = np.argsort(knorm.flatten())
        ax1.loglog(kvals, Abins, color=color, label=label)
        #ax2.semilogx(kvals, Abins, color=color, label=label)
    #
    ax1.set_xlabel("$k$")
    ax1.set_ylabel("$P(k)$")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(output_prefix+"PSD_loglog.png", dpi = 300, bbox_inches = "tight")
    plt.close(fig1)

    #ax2.set_xlabel("$k$")
    #ax2.set_ylabel("$P(k)$")
    #ax2.legend()
    #fig2.tight_layout()
    #fig2.savefig(output_prefix+"PSD_semilogx.png", dpi = 300, bbox_inches = "tight")
    #plt.close(fig2)

    return
