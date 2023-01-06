#from importlib import reload
#import sys
#sys.path.insert(0, '/home/dpe000/EnGIOPS/python')

import netCDF4
import numpy as np
import scipy.interpolate as si

crs_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0/SAM2/20220601/DIA/ORCA025-CMC-ANAL_1d_gridT-RUN-crs_20220531-20220606.nc'
dia_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0/SAM2/20220601/DIA/ORCA025-CMC-ANAL_1h_grid_T_2D_2022060100.nc'

def read_sam2_grid(file, fld='thetao'):
    dataset = netCDF4.Dataset(file)
    TM=dataset.variables[fld][:]
    lat=dataset.variables['nav_lat'][:]
    lon=dataset.variables['nav_lon'][:]
    #
    # NEED TO TRANSPOSE TO FIT Standard File Standard of (x,y)
    if ( TM.ndim == 4 ): TM=np.transpose(TM, (0, 1, 3, 2))
    if ( TM.ndim == 3 ): TM=np.transpose(TM, (0, 2, 1))
    if ( TM.ndim == 2 ): TM=np.transpose(TM, (1, 0))

    lat=np.transpose(lat)
    lon=np.transpose(lon)
    
    return lon, lat, TM

def map_dia_to_crs(dia):
    if ( dia.ndim > 2 ):
        # recursively loop mapping
        crs_list = []
        for iz in range(dia.shape[0]):
             crs_list.append(map_dia_to_crs(dia[iz]))
        crs = np.array(crs_list)
    else:
        nxd, nyd = dia.shape
        nxr = int((nxd - 2)/3) + 2
        nyr = int((nyd - 1)/3) + 2
        nxm = int(nxr/2)
    
        crs = np.zeros((nxr,nyr))
    
        crs[1:-1, 1:-1] = dia[1:-1:3, 1:-1:3]
    
        # APPLY EAST/WEST CYCLIC CONDITIONS
        crs[0,:] = crs[-2,:]
        crs[-1,:] = crs[1,:]
    
        # APPLY NORTH FOLD CONDITIONS
        # LAST LINE IS E/W flip of 3rd last line
        crs[-1:0:-1,-1] = crs[1:,-3]
        crs[0,-1] = crs[-2,-1]
    
        # 2ND LAST LINE IS E/W flip of self
        crs[-1:nxm:-1,-2] = crs[1:nxm,-2]
        crs[-1:nxm:-1,-2] = crs[1:nxm,-2]
    return crs


def simple_interp(crs, latlon_crs, latlon_dia, method='nearest', fill_value=0):   # methods are nearest, linear and cubic  (I think)
    lon_crs = latlon_crs[0]
    lat_crs = latlon_crs[1]

    lon_dia = latlon_dia[0]
    lat_dia = latlon_dia[1]
    
    lon_flat = lon_crs.flatten()
    lat_flat = lat_crs.flatten()
    if ( crs.ndim == 2 ):
        crs_flat = crs.flatten()
        dia = si.griddata( (lon_flat,  lat_flat), crs_flat, (lon_dia, lat_dia), method=method, fill_value=fill_value)
    else:
        dia_list = []
        for iz in lev(crs):
            dia_list.append(simple_interp(crs[iz], latlon_crs, latlon_dia, method=method, fill_value=fill_value))
        dia = np.array(dia_list)
        return
    return dia

def read_orca025_mask(var='tmask'):
    site='/space/hall5/sitestore'
    ubu='env_rhel-8-icelake-64'
    dire=site+'/eccc/mrd/rpnenv/socn000/'+ubu+'/datafiles/constants/oce/repository/master/CONCEPTS/orca025/grids'
    file=dire+'/mask_float.nc'
    #print('Mask file = '+ file)
    dataset = netCDF4.Dataset(file) 
    mask=np.squeeze(dataset.variables[var][:])
    mask=np.moveaxis(mask, [0, 1, 2], [0, 2, 1])
    return mask   # 3D ORCA025 mask  (1 = OCEAN)
    
def make_crs_mask(var='tmask'):
    mask_dia = read_orca025_mask(var=var)
    mask_crs = map_dia_to_crs(mask_dia)
    return mask_crs  # 3D CRS mask  (1 = OCEAN)

mask_crs_3d = make_crs_mask()
mask_dia_3d = read_orca025_mask()
mask_crs_2d = mask_crs_3d[0]
mask_dia_2d = mask_dia_3d[0]
    
def masked_interp(crs_2d, latlon_crs, latlon_dia, mskin_crs_2d=mask_crs_2d, mskout_dia_2d=mask_dia_2d ):
    lon_crs = latlon_crs[0]
    lat_crs = latlon_crs[1]

    lon_dia = latlon_dia[0]
    lat_dia = latlon_dia[1]
        
    if ( crs_2d.ndim > 2 ):
        print("NOT SURE IF 3RD DIMENSION WILL BE TIME OR ZED")
        return None
    
    IOCN = np.where( mskin_crs_2d == 1 )  # OCEAN POINTS
    lon_ocn = lon_crs[IOCN]
    lat_ocn = lat_crs[IOCN]
    crs_ocn = crs_2d[IOCN]
    
    dia_linear = simple_interp(crs_2d, latlon_crs, latlon_dia, method='linear', fill_value=np.NaN)
    dia_nearest =  simple_interp(crs_2d, latlon_crs, latlon_dia, method='nearest')
    # LINEAR WILL NOT EXTRAPOLATE -- NEAREST WILL.  REPLACE NAN in LINEAR INTERPOLATION WITH NEAREST NEIGHBOUR VALUES 
    # VALUES AT ENDS OF BAYS / NEAR COAST THAT LINEAR WOULD LEAVE AS NaN are now NEAREST CRS POINT -- OTHERWISE LINEAR COMBINATION OF CRS PTS.
    dia_interp = dia_linear.copy()
    IFILL = np.where(np.isnan(dia_linear))
    dia_interp[IFILL] = dia_nearest[IFILL]
    INAN = np.where(np.isnan(dia_linear))
    if ( len(INAN[0]) > 0 ):
        print("Interpolation still has NaN's")
        print(INAN)
    else:
        print(INAN)
    # MASK FINAL OUTPUT WITH DESTINATION MASK
    mask_dest=(1-mskout_dia_2d).astype(bool)
    print( dia_interp.shape, mask_dest.shape, type(dia_interp), type(mask_dest) )
    dia_masked=np.ma.array(dia_interp, mask=mask_dest )
    return dia_masked

def test():        
    dia_lon, dia_lat, dia_ssh = read_sam2_grid(dia_file,fld='zos')
    crs_lon, crs_lat, crs_ssh = read_sam2_grid(crs_file,fld='SSHN')
    crs_lon, crs_lat, crs_hbar = read_sam2_grid(crs_file,fld='HBAR')


    chk_lon = map_dia_to_crs(dia_lon)
    chk_lat = map_dia_to_crs(dia_lat)

    print( np.where(chk_lon - crs_lon != 0 ) )
    print( np.where(chk_lat - crs_lat != 0 ) )

    HBAR_2D = np.squeeze(crs_hbar)   #   HBAR is 3d with a trivial time dimension
    # THE FIRST ROW (j=0) of the CRS GRID IS MASKED (and this is the only place it is masked).
    #  CREATES PROBLEMS -- SET TO ZERO.
    NOTOK = np.where(HBAR_2D.mask == True)
    HBAR_2D[NOTOK] = 0.0

    HBAR_NEAR = simple_interp( HBAR_2D, (crs_lon, crs_lat), (dia_lon, dia_lat), method='nearest')
    HBAR_BLIN = simple_interp( HBAR_2D, (crs_lon, crs_lat), (dia_lon, dia_lat), method='linear')
    HBAR_MASK = masked_interp( HBAR_2D, (crs_lon, crs_lat), (dia_lon, dia_lat) , mskin_crs_2d=mask_crs_2d, mskout_dia_2d=mask_dia_2d)

    print('CRS', np.mean(crs_hbar), np.max(crs_hbar), np.min(crs_hbar))
    print('NEAREST', np.mean(HBAR_NEAR), np.max(HBAR_NEAR), np.min(HBAR_NEAR) )
    print('LINEAR', np.mean(HBAR_BLIN), np.max(HBAR_BLIN), np.min(HBAR_BLIN) )
    print('MASKED', np.mean(HBAR_MASK), np.max(HBAR_MASK), np.min(HBAR_MASK) )


# PLOT AND COMPARE
    return
