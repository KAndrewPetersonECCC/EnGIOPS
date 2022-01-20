import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import netCDF4

import read_dia
import datadatefile
import isoheatcont

stofile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_STOP/SAM2/20190313.10/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'
reffile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_DNH0/SAM2/20190313/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'

cmap_anom = 'seismic'
cmap_posd = 'gist_stern_r'

def plot_ens_diff(stofile, reffile=reffile)
    lon, lat, TM_sto, SW_sto = read_dia.read_sam2_grid_t(stofile)
    lon, lat, TM_ref, SW_ref = read_dia.read_sam2_grid_t(reffile)

    TM_dif = TM_sto-TM_ref
    SW_dir = SW_sto-SW_ref
    
    

    print('SHAPE', TM_dif.shape)
    print('Max/Min', np.max(TM_dif), np.min(TM_dif))

    CLEV=np.arange(-0.9,1.1,0.2)        
    
    title='Anomaly of Stochastic Case'
    cplot.grd_pcolormesh(lon, lat, TM_dif[0,0,:,:], levels=CLEV, cmap=cmap_anom, outfile='TM_dif.png', project='PlateCarree', title=title, obar='horizontal')

    return
