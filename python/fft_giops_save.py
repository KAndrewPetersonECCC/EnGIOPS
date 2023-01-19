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

dmap='gist_stern_r'
dmap='gist_stern'

mdir3='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_hub/'
mdir4='/fs/site4/eccc/mrd/rpnenv/dpe000/maestro_hub/'

CIOPS_box = [-60, -20, 40, 60]  # I DONT ACTUALLY REMEMBER WHAT THE CIOPS BOX IS
SAMBLE_LL_SWS=(-51.0, 44.0)
SAMPLE_box = [(-51.00000000000000, 44.00000000000000), 
              (-38.67012447546572, 43.33026327866403), 
                  (-36.36598884704791, 52.08293473102154), 
                  (-51.00000000000000, 52.99642502121892), 
                  (-51.00000000000000, 44.00000000000000)]
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

def read_anl_velocity(date, dir=''):
    lead_str = str(0).zfill(3)
    date_str = date.strftime("%Y%m%d%H") 
    file=dir+date_str+"_"+lead_str
    klev, UU = read_var.read_3D_lev(file, 'UUW', 0)
    klev, VV = read_var.read_3D_lev(file, 'VVW', 0)
    return (UU,VV) 

def read_rmn_velocity(date, Ndays=29, dir=mdir5):
    if ( (Ndays-1)%2 != 0 ): 
        print("Ndays must be odd -- adding 1")
        Ndays = Ndays+1
    Nhalf = (Ndays-1) / 2
    Adays = np.arange(Ndays).astype(int) - Nhalf
    UU_list = []
    VV_list = []
    for day in Adays:
        this_date = date+datetime.timedelta(days=day)
        UU, VV = read_anl_velocity(this_date, dir=dir)
        UU_list.append(UU)
        VV_list.append(VV)
    UU_mean = sum(UU_list) / Ndays
    VV_mean = sum(VV_list) / Ndays

    UU_sqr = []
    VV_sqr = []
    for iday in range(Ndays):
        UU = UU_list[iday] - UU_mean
        VV = VV_list[iday] - VV_mean
        UU_sqr.append( np.square(UU) )
        VV_sqr.append( np.square(VV) )
    UU_vari = sum(UU_sqr) / Ndays
    VV_vari = sum(VV_sqr) / Ndays
    return (UU_mean, VV_mean), (UU_vari, VV_vari)
       
     
def read_ens_mean_velocity(date, leadhr, dir=mdir5, ensembles=range(21)):
    lead_str = str(leadhr).zfill(3)
    date_str = date.strftime("%Y%m%d%H") 
    UU_ens = []
    VV_ens = []
    ne=len(ensembles)
    for ens in ensembles:
        ensm_str=str(ens).zfill(3)
        file=dir+date_str+"_"+lead_str+"_"+ensm_str
        klev, UU = read_var.read_3D_lev(file, 'UUW', 0)
        klev, VV = read_var.read_3D_lev(file, 'VVW', 0)
        UU_ens.append(UU)
        VV_ens.append(VV)
        
    UU_mean = sum(UU_ens) / len(UU_ens)
    VV_mean = sum(VV_ens) / len(VV_ens)
    
    #UU_ano = []
    #VV_ano = []
    UU_sqr = []
    VV_sqr = []
    for iens in range(ne):
        UU = UU_ens[iens] - UU_mean
        VV = VV_ens[iens] - VV_mean
        #UU_ano.append( UU )
        #VV_ano.append( VV )
        UU_sqr.append( np.square(UU) )
        VV_sqr.append( np.square(VV) )
        
    UU_vari = sum(UU_sqr) / len(UU_sqr)
    VV_vari = sum(VV_sqr) / len(VV_sqr)
    
    return (UU_mean, VV_mean), (UU_vari, VV_vari)
            
def draw_box(ax, box, color='b'):
    x_box = [ corner[0] for corner in box ]
    y_box = [ corner[1] for corner in box ]
    ax.plot(x_box, y_box, color=color, linestyle='-', transform=ccrs.Geodetic() )
    return ax
    
def pcolormesh_with_box(lon, lat, field, levels=None, ticks=None, cmap=dmap, project='PlateCarree', 
                        outfile='plt.png', box=CIOPS_box, 
                        make_global=False, title='', cbar=True, obar='vertical', 
                        plot_boxes=[SAMPLE_box], box_colors=['b'], **kwargs):

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
    ax.set_title(title)
    fig.savefig(outfile,bbox_inches='tight')
    plt.close(fig)
    return

def interpolate_to_box(FLD, LL_mod, LL_box, method='nearest'):
    lon_mod, lat_mod = LL_mod
    lon_box, lat_box = LL_box
    #
    FLD_box = scipy.interpolate.griddata( (lon_mod.flatten(), lat_mod.flatten()), FLD.flatten(), (lon_box, lat_box), method='nearest')
    return FLD_box
    
def get_fft_ps(KE_grid):
    KE_FFT = np.fft.fft2(KE_grid)
    #ps = np.abs(KE_FFT)**2   #  Potentially need to provide a normalization
    ps = get_psd(KE_FFT)
    return ps, KE_FFT

def get_psd(KE_FFT):
    ps = np.abs( KE_FFT * np.conj(KE_FFT) )
    return ps

def find_wavenumber_norm(N, grid_step):
    wavenumber = 2 * np.pi * np.fft.fftfreq(N, grid_step)
    K2D = np.meshgrid(wavenumber, wavenumber)
    knorm = np.sqrt(K2D[0]**2 +K2D[1]**2)
    return knorm

def setup_Kbins(N, grid_step):
    kbins = 2 * np.pi * np.arange(0.5, N/2., 1.)/(grid_step*N/np.sqrt(2))
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

def loop_dates_test(date_range, lead_hr, data_dir=mdir5, anal_dir=mdir5):
    date_begin=date_range[0]
    date_final=date_range[1]
    
    date_fina_seconds = seconds_since_epoch(date_final)
    date_loop=date_begin
    date_loop_seconds = seconds_since_epoch(date_loop)
    
    nday = 0    
    while ( date_loop_seconds <= date_fina_seconds ):
        print(date_loop.strftime('%Y%m%d%H'))
        date_anal=date_loop + datetime.timedelta(hours=lead_hr)
        try:
            (UU_mean, VV_mean), (UU_vari, VV_vari) =  read_ens_mean_velocity(date_loop, lead_hr, dir=data_dir)
            (UU_anal, VV_anal) = read_anl_velocity(date_anal, dir=anal_dir)
            (UU_time, VV_time), (UU_vart, VV_vart) =  read_rmn_velocity(date_loop, dir=anal_dir)
        except:
            print("Failure at "+date_loop.strftime('%Y%m%d%H'))
            return False    
        date_loop = date_loop + datetime.timedelta(days=1)
        date_loop_seconds = seconds_since_epoch(date_loop)
        nday = nday + 1

    return True

def calc_KE(date_loop, lead_hr, GRIDS, data_dir=mdir5, anal_dir=mdir5):
    date_anal=date_loop + datetime.timedelta(hours=lead_hr)
    (UU_mean, VV_mean), (UU_vari, VV_vari) =  read_ens_mean_velocity(date_loop, lead_hr, dir=data_dir)
    (UU_anal, VV_anal) = read_anl_velocity(date_anal, dir=anal_dir)
    (UU_erro, VV_erro) = (UU_mean-UU_anal, VV_mean-VV_anal)
    (UU_time, VV_time), (UU_vart, VV_vart) =  read_rmn_velocity(date_loop, dir=anal_dir)
    
    KE_vari = 0.5 * ( UU_vari+VV_vari )
    KE_vart = 0.5 * ( UU_vart+VV_vart )
    KE_erro = 0.5 * ( np.square(UU_erro) + np.square(VV_erro) )

    return KE_vari, KE_vart, KE_erro
    
def calc_date(date_loop, lead_hr, GRIDS, data_dir=mdir5, anal_mdir5=mdir5):
    
    print(date_loop.strftime('%Y%m%d%H'))
    KE_vari, KE_vart, KE_erro = calc_KE(date_loop, lead_hr, GRIDS, data_dir=data_dir, anal_dir=anal_dir)

    # initialize list of FFT's
    FFT_DATE = []
    PS_DATE = []
    for igrid, llgrid in enumerate(GRIDS):
        FFT_GRID = []
        PS_GRID = []
        for ik, KE in enumerate([KE_vari, KE_vart, KE_erro]):
            KE_box = interpolate_to_box( KE, (lon, lat), llgrid)
            ps, KE_FFT = get_fft_ps(KE_box)
            FFT_GRID.append(KE_FFT)
            PS_GRID.append(ps)
        FFT_DATE.append(FFT_GRID)
        PS_DATE.append(PS_GRID)

    return (FFT_DATE, PS_DATE), (KE_vari, KE_vart, KE_erro)

def init_FFT_sum(GRIDS, nffts=3):

    ngrids = len(GRIDS)
    
    # initialize list of FFT's
    FFT_SUM = []
    PS_SUM = []
    for llgrid in GRIDS:
       FFT_GRID = []
       PS_GRID = []
       for iKE in range(nffts):
           nx, ny = llgrid[0].shape
           FFT_GRID.append(np.zeros((nx, ny)).astype(complex))
           PS_GRID.append(np.zeros((nx,ny)).astype(float))
       FFT_SUM.append(FFT_GRID)
       PS_SUM.append(PS_GRID)
    return (FFT_SUM, PS_SUM)


def addto_FFT_sum(niter, FFTPS_SUM, FFTPS_DATE ):
    (FFT_SUM, PS_SUM) = FFTPS_SUM
    (FFT_DATE, PS_DATE) = FFTPS_DATE
    ngrids=len(FFT_DATE)
    nffts=len(FFT_DATE[0])
    
    for igrid in range(ngrids):
        for ifft in range(nffts):
            FFT_SUM[igrid][ifft] = FFT_SUM[igrid][ifft] + FFT_DATE[igrid][ifft]
            PS_SUM[igrid][ifft] = PS_SUM[igrid][ifft] + PS_DATE[igrid][ifft]

    # I might as well finally learn these C constructs (niter = niter+1)
    niter+=1
    
    return niter, (FFT_SUM, PS_SUM)

def final_FFT_mean(niter, FFTPS_SUM ):
    (FFT_SUM, PS_SUM) = FFTPS_SUM
    ngrids=len(FFT_SUM)
    nffts=len(FFT_SUM[0])
    print('N = '+str(niter))

    PS_MEAN = []
    for igrid in range(ngrids):
        PS_GRID = []
        for ifft in range(nffts):
            FFT_THIS = FFT_SUM[igrid][ifft] / niter
            FFT_SUM[igrid][ifft] = FFT_THIS
            PS_SUM[igrid][ifft] = PS_SUM[igrid][ifft] / niter
            PS_THIS = get_psd(FFT_THIS)
            PS_GRID.append(PS_THIS)
        PS_MEAN.append(PS_GRID)

    # I am pretty sure we want the PS from mean FFT, but the mean PS (sum of squares/no wave cancellation) might be useful too.
    return (FFT_SUM, PS_SUM, PS_MEAN)
            
def init_KE_sum(KE_list):
    sum_KE_list = []
    for KE in KE_list:
        sum_KE = np.zeros(KE.shape)
        sum_KE_ma = np.ma.array(sum_KE, mask=KE.mask)
        sum_KE_list.append(sum_KE_ma)
    return sum_KE_list
                
def addto_KE_sum(niter, SUM_KE_list, KE_list):
    nlist = len(KE_list)
    for iKE in range(nlist):
        SUM_KE_list[iKE] = SUM_KE_list[iKE] + KE_list[iKE]
    niter+=1
    return niter, SUM_KE_list

def final_KE_mean(niter, SUM_KE_list):
    MEAN_KE_list = []
    print('N = '+str(niter))
    for KE in SUM_KE_list:
        MEAN_KE = KE / niter
        MEAN_KE_list.append(MEAN_KE)
    return MEAN_KE_list   
        
               
           
def loop_dates(date_range, lead_hr, data_dir=mdir5, anal_dir=mdir5, grid_step=5.0):
    nffts = 3 
    
    date_begin=date_range[0]
    date_final=date_range[1]
    date_begin_str = date_begin.strftime("%Y%m%d%H") 
    date_final_str = date_final.strftime("%Y%m%d%H") 
    date_string = date_begin_str+'_'+date_final_str
    
    date_fina_seconds = seconds_since_epoch(date_final)
    date_loop=date_begin
    date_loop_seconds = seconds_since_epoch(date_loop)
    
    #(LL_GRID1, LL_GRID2, LL_GRID3), (LL_box1, LL_box2, LL_box3) = boxes()
    GRIDS, BOXES = boxes(grid_step=grid_step)
    ngrids=len(GRIDS)

    # initialize list of FFT's
    (FFT_SUM, PS_SUM) = init_FFT_sum(GRIDS, nffts=nffts)
    
    nday = 0
    ndaw = 0    
    while ( date_loop_seconds <= date_fina_seconds ):

        (FFT_DATE, PS_DATE), (KE_vari, KE_vart, KE_erro) = calc_date(date_loop, lead_hr, GRIDS, data_dir=data_dir, anal_dir=anal_dir)
        if (ndaw == 0):
            # initialize KE_SUM
            (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro) = init_KE_sum((KE_vari, KE_vart, KE_erro))
        # addto_FFT_sum iterates nday as well.  
        nday, (FFT_SUM, PS_SUM) = addto_FFT_sum(nday, (FFT_SUM, PS_SUM), (FFT_DATE, PS_DATE) )
        ndaw, (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro) = addto_KE_sum(ndaw, [KE_vari, KE_vart, KE_erro] )
        
        date_loop = date_loop + datetime.timedelta(days=1)
        date_loop_seconds = seconds_since_epoch(date_loop)
        #nday = nday + 1  # done in addto_FFT_sum

    ## Mean of FFT's , Mean of PS's (sum of squares), PS from mean FFT (wave cancellation)
    FFT_MEAN, PS_RMSS, PS_MEAN = final_FFT_mean(nday, (FFT_SUM, PS_SUM) )
    (MEAN_KE_vari, MEAN_KE_vart, MEAN_KE_erro) = final_KE_mean(ndaw, (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro))
    
    plot_all_psd( (ngrids, nffts), PS_MEAN, grid_step=grid_step, out_dir='ENS_FFT/ENS_FFT/'+date_string+'_')    
                      
    return (FFT_MEAN, PS_MEAN)

def mean_dates(date_range, lead_hr, data_dir=mdir5, anal_dir=mdir5, grid_step=5.0, out_dir='ENS_FFT/ENS_FFT/'):
    
    date_begin=date_range[0]
    date_final=date_range[1]
    date_begin_str = date_begin.strftime("%Y%m%d%H") 
    date_final_str = date_final.strftime("%Y%m%d%H") 
    date_string = date_begin_str+'_'+date_final_str
    lead_str = str(lead_hr).zfill(3)
        
    date_fina_seconds = seconds_since_epoch(date_final)
    date_loop=date_begin
    date_loop_seconds = seconds_since_epoch(date_loop)
    
    #(LL_GRID1, LL_GRID2, LL_GRID3), (LL_box1, LL_box2, LL_box3) = boxes()
    GRIDS, BOXES = boxes(grid_step=grid_step)
    ngrids=len(GRIDS)
    nffts=3

    # initialize list of FFT's
    (FFT_SUM, PS_SUM) = init_FFT_sum(GRIDS, nffts=nffts)
    
    nday = 0    
    ndaw = 0
    while ( date_loop_seconds <= date_fina_seconds ):

        (FFT_DATE, PS_DATE) = read_FFT_DATE(date_loop, lead_hr=lead_hr, out_dir=out_dir)
        (KE_vari, KE_vart, KE_erro) = read_KE_DATE(date_loop, lead_hr=lead_hr, 
                                                   var_list=('KE_vari', 'KE_vart', 'KE_erro'), 
                                                   out_dir=out_dir)
        if (ndaw == 0):
            # initialize KE_SUM
            (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro) = init_KE_sum((KE_vari, KE_vart, KE_erro))
        # addto_FFT_sum iterates nday as well.  
        nday, (FFT_SUM, PS_SUM) = addto_FFT_sum(nday, (FFT_SUM, PS_SUM), (FFT_DATE, PS_DATE) )
        ndaw, (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro) = addto_KE_sum(ndaw, [SUM_KE_vari, SUM_KE_vart, SUM_KE_erro], [KE_vari, KE_vart, KE_erro] )
            
        date_loop = date_loop + datetime.timedelta(days=1)
        date_loop_seconds = seconds_since_epoch(date_loop)
        
    ## Mean of FFT's , Mean of PS's (sum of squares), PS from mean FFT (wave cancellation)
    FFT_MEAN, PS_RMSS, PS_MEAN = final_FFT_mean(nday, (FFT_SUM, PS_SUM) )
    (MEAN_KE_vari, MEAN_KE_vart, MEAN_KE_erro) = final_KE_mean(ndaw, (SUM_KE_vari, SUM_KE_vart, SUM_KE_erro) )
    
    plot_all_psd( (ngrids, nffts), PS_MEAN, grid_step=grid_step, out_dir=out_dir+date_string+'_'+lead_str+'_') 

    CLEVEL = np.arange(0, 0.1025, 0.0025)
    CTICKS= np.arange(0, 0.11, 0.01)
    for iKE, KE in enumerate((MEAN_KE_vari, MEAN_KE_vart, MEAN_KE_erro)):
        if ( iKE == 0 ):  
            KE_str='KE_EVar'
        if ( iKE == 1 ):  
            KE_str='KE_Tvar'
        if ( iKE == 2 ):  
            KE_str='KE_RMSE'
      
        outfile=out_dir+KE_str+'_'+date_string+'_'+lead_str+'.png'
        pcolormesh_with_box(lon, lat, KE, levels=CLEVEL, ticks=CTICKS, cmap=dmap, project='Mercator', outfile=outfile, box=CIOPS_box, cbar=True, 
                            obar='horizontal', plot_boxes=BOXES, box_colors=['r', 'b', 'g'])
                      
    return
    
def plot_all_psd( grids_and_ffts, PS_MEAN, grid_step=5.0, out_dir='ENS_FFT/ENS_FFT/'):
    (ngrids, nffts) = grids_and_ffts
    #
    for igrid in range(ngrids):
        box_str = 'Box'+str(igrid)
        PS_GRID = PS_MEAN[igrid]
        plot_psd_multi(PS_GRID, grid_step, 
                       labels=['Ensemble Variance', 'Temporal Variance', 'Forecast Error'], 
                       output_prefix=out_dir+box_str+'.'
                      )
                      
    for ifft in range(nffts):
        if ( ifft == 0 ):  KE_str='EVar'
        if ( ifft == 1 ):  KE_str='Tvar'
        if ( ifft == 2 ):  KE_str='RMSE'
        PS_KE = [ PS_MEAN[igrid][ifft] for igrid in range(ngrids)]
        plot_psd_multi(PS_KE, grid_step, 
                       labels=['Box 1', 'Box 2', 'Box 3'], 
                       output_prefix=out_dir+KE_str+'.'
                      )
    #
    return

def single_date_and_save(date_loop, lead_hr, grid_step=5.0, data_dir=mdir5, anal_dir=mdir5, out_dir='ENS_FFT/ENS_FFT/'):
    nffts = 3 
    
    #(LL_GRID1, LL_GRID2, LL_GRID3), (LL_box1, LL_box2, LL_box3) = boxes()
    GRIDS, BOXES = boxes(grid_step=grid_step)
    ngrids = len(GRIDS)
    (FFT_DATE, PS_DATE), (KE_vari, KE_vart, KE_erro) = calc_date(date_loop, lead_hr, GRIDS, data_dir=data_dir, anal_dir=anal_dir)
    rc = write_FFT_DATE(date_loop, lead_hr, FFT_DATE, out_dir=out_dir)
    rc = write_KE_DATE(date_loop, lead_hr, (KE_vari, KE_vart, KE_erro), ('KE_vari', 'KE_vart', 'KE_erro'), out_dir=out_dir)
    #
    date_str = date_loop.strftime("%Y%m%d%H") 
    lead_str = str(lead_hr).zfill(3)
    plot_all_psd( (ngrids, nffts), PS_DATE, grid_step=grid_step, out_dir=out_dir+date_str+'_'+lead_str+'_') 
    CLEVEL = np.arange(0, 0.1025, 0.0025)
    CTICKS= np.arange(0, 0.11, 0.01)
    for iKE, KE in enumerate((KE_vari, KE_vart, KE_erro)):
        if ( iKE == 0 ):  KE_str='KE_EVar'
        if ( iKE == 1 ):  KE_str='KE_Tvar'
        if ( iKE == 2 ):  KE_str='KE_RMSE'
      
        outfile=out_dir+KE_str+'_'+date_str+'_'+lead_str+'.png'
        pcolormesh_with_box(lon, lat, KE, levels=CLEVEL, ticks=CTICKS, cmap=dmap, project='PlateCarree', outfile=outfile, box=CIOPS_box, cbar=True, 
                            obar='horizontal', plot_boxes=BOXES, box_colors=['r', 'b', 'g'])
    return   

def write_FFT_DATE(date_loop, lead_hr, FFT_DATE, out_dir='ENS_FFT/ENS_FFT/'):
    #
    date_str = date_loop.strftime("%Y%m%d%H") 
    lead_str = str(lead_hr).zfill(3)
    file=out_dir+'FFT_'+date_str+'_'+lead_str+'.nc'
    #
    ngrids=len(FFT_DATE)
    nffts=len(FFT_DATE[0])
    
    NCVAR=[]
    FFTRV=[]
    DIMGG=[]
    for igrid in range(ngrids):
        NCVAR_G=[]
        FFTRV_G=[]
        (nx, ny) = FFT_DATE[igrid][0].shape
        DIMGG.append((nx,ny))
        for ifft in range(nffts):
            if ( ifft == 0 ):  KE_str='EVar'
            if ( ifft == 1 ):  KE_str='Tvar'
            if ( ifft == 2 ):  KE_str='RMSE'
            ReFFT = FFT_DATE[igrid][ifft].real
            ImFFT = FFT_DATE[igrid][ifft].imag
            FFTRV_G.append(ReFFT)
            FFTRV_G.append(ImFFT)
            NCVAR_G.append(KE_str+'R'+str(igrid))
            NCVAR_G.append(KE_str+'I'+str(igrid))
        NCVAR.append(NCVAR_G)
        FFTRV.append(FFTRV_G)
    rc = write_nc_grid.write_nc_multi_grid(DIMGG, FFTRV, NCVAR, file)
    return rc
        
def read_FFT_DATE(date_loop, lead_hr=72, out_dir='ENS_FFT/ENS_FFT/'): 
    ngrids=3
    date_str = date_loop.strftime("%Y%m%d%H")
    lead_str = str(lead_hr).zfill(3) 
    file=out_dir+'FFT_'+date_str+'_'+lead_str+'.nc'
    vars=['EVarR', 'EVarI', 'TvarR', 'TvarI', 'RMSER', 'RMSEI']
    nffts=len(vars)/2
    
    FFT_DATE = []
    PS_DATE = []
    for igrid in range(ngrids):
        gvars = [ vars[ivar]+str(igrid) for ivar in range(nffts*2)]
        FFT_READ = write_nc_grid.read_nc(file, gvars)
        FFT_GRID = []
        PS_GRID = []
        for ifft in range(nffts):
            FFT_real = FFT_READ[2*ifft]
            FFT_imag = FFT_READ[2*ifft+1]
            FFT_THIS=FFT_real.astype(complex)+1j*FFT_imag.astype(complex)
            FFT_GRID.append(FFT_THIS)
            PS_THIS = get_psd(FFT_THIS)
            PS_GRID.append(PS_THIS)
        FFT_DATE.append(FFT_GRID)
        PS_DATE.append(PS_GRID)
        
    return (FFT_DATE, PS_DATE)

def write_KE_DATE(date_loop, lead_hr, KE_list, var_list, out_dir='ENS_FFT/ENS_FFT/'):
    date_str = date_loop.strftime("%Y%m%d%H")
    lead_str = str(lead_hr).zfill(3) 
    file=out_dir+'KE_'+date_str+'_'+lead_str+'.nc'
    rc = write_nc_grid.write_nc_grid(KE_list, var_list, file)
    return rc

def read_KE_DATE(date_loop, lead_hr, var_list, out_dir='ENS_FFT/ENS_FFT/'):
    date_str = date_loop.strftime("%Y%m%d%H")
    lead_str = str(lead_hr).zfill(3) 
    file=out_dir+'KE_'+date_str+'_'+lead_str+'.nc'
    KE_list = write_nc_grid.read_nc(file, var_list)
    return KE_list

def boxes(grid_step=5.0):
    LL_SW1=(-58.9, 35.1); THETA1=-30; LENGTH1=970.0
    LLGRID1, LL_box1 = create_box( LL_SW1, size=LENGTH1, dx=grid_step, theta=THETA1 )
    LL_SW2=(-68.5, 35.1); THETA2=-3; LENGTH2=900.0
    LLGRID2, LL_box2 = create_box( LL_SW2, size=LENGTH2, dx=grid_step, theta=THETA2 )
    LL_SW3=(-52.0, 44.0); THETA3=-3; LENGTH3=1000.0
    LLGRID3, LL_box3 = create_box( LL_SW3, size=LENGTH3, dx=grid_step, theta=THETA3 )
    return (LLGRID1, LLGRID2, LLGRID3), (LL_box1, LL_box2, LL_box3)
        
def test_routine():
    date=datetime.datetime(2019, 7, 16, 0, 0, 0, 0, utc)
    leadhr=72

    (UU_mean, VV_mean), (UU_vari, VV_vari) =  read_ens_mean_velocity(date, leadhr, dir=mdir5)
    KE_vari = 0.5 * ( UU_vari+VV_vari )
    KE=KE_vari
    
    (X, Y, zone, name) = utm.from_latlon(lat, lon)
    LAT, LON = utm.to_latlon(X, Y, zone, name,strict=False)

    fig, ax = plt.subplots()
    ax.pcolormesh(X, Y, KE)
    fig.savefig('KE_UTMgrid.png')
    plt.close(fig)

    grid_step = 5 # km
    (LLGRID1, LLGRID2, LLGRID3), (LL_box1, LL_box2, LL_box3) = boxes(grid_step=grid_step)
    
    print('BOX 1' )
    print( LL_box1 )
    print( grid_box_corners(LLGRID1) )
    print( 'BOX 2' )
    print( LL_box2 )
    print( grid_box_corners(LLGRID2) )
    print( 'BOX 3' )
    print( LL_box3 )
    print( grid_box_corners(LLGRID3))

    KE_box1 = interpolate_to_box( KE, (lon, lat), LLGRID1)
    KE_box2 = interpolate_to_box( KE, (lon, lat), LLGRID2)
    KE_box3 = interpolate_to_box( KE, (lon, lat), LLGRID3)

    pcolormesh_with_box(lon, lat, KE, levels=None, ticks=None, cmap=dmap, project='PlateCarree', outfile='KE_CIOPS.png', box=CIOPS_box, cbar=True, 
                        obar='horizontal', plot_boxes=[LL_box1, LL_box2, LL_box3], box_colors=['r', 'b', 'g'])


    grid_step = 5 # km

    ps1, KE_FFT_box1 = get_fft_ps(KE_box1)
    ps2, KE_FFT_box2 = get_fft_ps(KE_box2)
    ps3, KE_FFT_box3 = get_fft_ps(KE_box3)

    plot_psd(ps1, grid_step, output_prefix='./box1_')
    plot_psd(ps2, grid_step, output_prefix='./box2_')
    plot_psd(ps3, grid_step, output_prefix='./box3_')

    plot_psd_multi([ps1, ps2, ps3], grid_step, labels=['Box 1', 'Box 2', 'Box 3'], output_prefix='./M.')

    print('PS1', np.max(ps1))
    print('PS2', np.max(ps2))
    print('PS3', np.max(ps3))

    return

