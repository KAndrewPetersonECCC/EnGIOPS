import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import netCDF4
import os.path

import cplot

file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/rms_ORCA025-CMC-ANAL_1d_grid_T_2020040100.nc'
def read_sam2_grid_t(file):
    dataset = netCDF4.Dataset(file)
    TM=dataset.variables['thetao'][:]
    SALW=dataset.variables['so'][:]
    lat=dataset.variables['nav_lat'][:]
    lon=dataset.variables['nav_lon'][:]
    #
    # NEED TO TRANSPOSE TO FIT Standard File Standard of (x,y)
    TM=np.transpose(TM, (0, 1, 3, 2))
    SALW=np.transpose(SALW, (0, 1, 3, 2))
    lat=np.transpose(lat)
    lon=np.transpose(lon)
    
    return lon, lat, TM, SALW

cmap_anom = 'seismic'
cmap_posd = 'gist_stern_r'
lon,lat,TM,SALW=read_sam2_grid_t(file)
#cplot.pcolormesh(lon, lat, TM[0,0,:,:], levels=np.arange(0,1.2,0.2), cmap=cmap_posd, outfile='TM_rmse.png',project='NorthPolarStereo',box=[-180, 180, 50, 90], title='SST Ensemble Standard Deviation')
cplot.pcolormesh(lon, lat, TM[0,0,:,:], levels=np.arange(0,2.2,0.2), cmap=cmap_posd, outfile='TM_rmse.png',project='PlateCarree',box=[-80, 20, 30, 80], title='SST Ensemble Standard Deviation', obar='horizontal')
