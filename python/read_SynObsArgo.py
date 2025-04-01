import sys
import numpy as np
#import matplotlib as mpl
#mpl.use('Agg')

import datetime
import pytz
import numbers

import xarray as xr

utc=pytz.timezone('UTC')

file='/fs/site6/eccc/mrd/rpnenv/dpe000/EN4/EN.4.2.2.f.profiles.g10.202212.nc'
dirEN='/fs/site6/eccc/mrd/rpnenv/dpe000/EN4'
REFERENCE_DATE = datetime.datetime(1950,1,1,0,0,0,0, pytz.UTC)

file='/home/dpe000/data/ppp6/SynObs2/5/OP-AN/GIOPS/CNTL/OPA-PL/ArRef/OPA-PL_ArRef_202001_GIOPS_CNTL.nc'
filf='/home/dpe000/data/ppp6/JAMSTEC_MIRROR/www.jamstec.go.jp/jcope/data/synobs_frontiers/OP-AN/FOAM/CNTL/OPA-PL/ArRef/OPA-PL_ArRef_202001_FOAM_CNTL.nc'

def read_argo(file):
    ARGO=xr.open_dataset(file)
    return ARGO
    
def read_argo_data(file, obs=False):
    ARGO=read_argo(file)
    TEMP=ARGO['T'].values
    SALW=ARGO['S'].values
    dept=ARGO['depth'].values
    time=ARGO['juld'].values
    
    lon=ARGO['longitude'].values
    lat=ARGO['latitude'].values
    WMO=ARGO['WMO_number'].values
    
    if ( obs ):
        TEMP_obs=ARGO['T_argo'].values
        SALW_obs=ARGO['S_argo'].values
        ARGO.close()
        return (lon, lat, time, dept), (TEMP, SALW), (TEMP_obs, SALW_obs)
        
    else:
        ARGO.close()
        return (lon, lat, time, dept), (TEMP, SALW)
        
