
import sys
this_dir='/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python_drew'
sys.path.insert(0, this_dir)
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import os.path
import netCDF4
import scipy.interpolate

nensembles=21
file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020110400.nc'

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
    
def read_sam2_grid_t(file):
    lon, lat, TM = read_sam2_grid(file,'thetao')
    __, __, SALW = read_sam2_grid(file, 'so')
    return lon, lat, TM, SALW

filu='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_U_2020110400.nc'
filv='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_V_2020110400.nc'
filh='fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1h_grid_T_2D_2020110400.nc'

def read_sam2_grid_u(filu):
    lonu, latu, UO = read_sam2_grid(filu, 'uo')
    return lonu, latu, U0

def read_sam2_grid_v(filv):
    lonv, latv, VO = read_sam2_grid(filu, 'vo')
    return lonv, latv, V0

def regrid_to_T((lon, lat), (lonu, latu, U0)):
   nt=1
   nz=1
   if ( U0.ndim == 4 ): nt, nz, nx, ny = U0.shape
   if ( U0.ndim == 3 ): nz, nx, ny = U0.shape
   if ( U0.ndim == 2 ): nx, ny = U0.shape

   UT = np.zeros((nt, nz, nx, ny))
   for it in range(nt):
     for iz in range(nz):
       if ( U0.ndim == 4 ):  UZ = U0[it, iz, :, :]
       if ( U0.ndim == 3 ):  UZ = U0[iz, :, :]
       if ( U0.ndim == 2 ):  UZ = U0[:, :]
       UT[it, iz, :, :] = scipy.interpolate.griddata((lonu.flatten(), latu.flatten()), UZ.flatten(), (lon,lat), method='linear', fill_value=0)
   UT = np.squeeze(UT)
   return UT

def regrid_UV((lon,lat), (lonu, latu, U0), (lonv, latv,V0) ):
    UT = np.zeros(U0.shape)
    UT = regrid_to_T((lon,lat), (lonu, latu, U0))
    VT = regrid_to_T((lon,lat), (lonv, latv, V0))
    return UT, VT

file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020110400.nc'
dir='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives'
ens_pre='GIOPS_E'
date=datetime.datetime(2020, 11, 04)

def read_ensemble(dir, ens_pre, date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_', ensembles=[]):

    if ( len(ensembles) == 0 ): ensembles=range(nensembles)
    datestr=date.strftime("%Y%m%d%H")
    datestd=datestr[:8]

    if ( fld == 'T' ): var='thetao'
    if ( fld == 'S' ): var='so'
    if ( fld == 'U' ): var='uo'
    if ( fld == 'V' ): var='vo'
    if ( fld == 'H' ): var='zos'

    grid='grid_'+fld
    if ( fld == 'S' ): grid='grid_'+'T'
    if ( fld == 'H' ): grid='grid_T_2D'
    FLD_ENSEMBLE = []
    for ens in ensembles:
        ensstr=str(ens)
	file=dir+'/'+ens_pre+ensstr+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc'
	print(file)
	lon, lat, FLD = read_sam2_grid(file, fld=var)
	FLD_ENSEMBLE.append(FLD)
    return lon, lat, FLD_ENSEMBLE
 
def ensemble_mean(FLD_ENSEMBLE):
    FLD_MEAN = sum(FLD_ENSEMBLE) / len(FLD_ENSEMBLE)
    return FLD_MEAN

def ensemble_anomaly(FLD_ENSEMBLE):
    FLD_MEAN = ensemble_mean(FLD_ENSEMBLE)
    FLD_ANOMALY=[member-FLD_MEAN for member in FLD_ENSEMBLE]
    return FLD_ANOMALY
    
def ensemble_square(FLD_ENSEMBLE):
    FLD_SQUARE=[np.square(member) for member in FLD_ENSEMBLE]
    return FLD_SQUARE
    
def ensemble_var(FLD_ENSEMBLE):
    FLD_ANOMALY = ensemble_anomaly(FLD_ENSEMBLE)
    FLD_SQUARE = ensemble_square(FLD_ANOMALY)
    FLD_VARIANCE = ensemble_mean(FLD_SQUARE)
    return FLD_VARIANCE
