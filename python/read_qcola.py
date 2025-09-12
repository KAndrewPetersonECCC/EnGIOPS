import sys
import os
import xarray as xr
import numpy as np
import glob
import check_date

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import create_dates

mdir = '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'

def obtain_files(date_range, expt, OLA='VP', trial='trial', ext='000', ddir=mdir):

    if ( isinstance(date_range, str) ):
        if ( date_range == '*' or date_range.casefold() == 'All'.casefold() ):
            date='????????'
            scan=ddir+'/'+expt+'/SAM2/'+date+'/DIAG/'+trial+'/'+date+ext+'_QCOLA_'+OLA+'_BEST.nc'
            print('ls '+scan)
            files = glob.glob(scan)
        return files
    if ( len(date_range) == 3 ):
        dates=create_dates.create_dates(date_range[0], date_range[1], date_range[2])
    elif ( len(date_range) == 2 ):
        dates=create_dates(date_range[0], date_range[1], 7)
    else:
        dates=date_range
        
    if ( isinstance(dates[0], str) ):
        dates_str = dates
    else:
        dates_str = check_date.check_date_list(dates, outtype=str, dtlen=8)
   

    files = []
    for date in dates_str:
        file = ddir+'/'+expt+'/SAM2/'+date+'/DIAG/'+trial+'/'+date+ext+'_QCOLA_'+OLA+'_BEST.nc'
        if os.path.isfile(file):
            files.append(file)
    
    return files

def read_VPOLA(files, group='VP/VP_GEN_INSITU_REALTIME'):

    VPxr = xr.open_mfdataset(files, group=group, combine='nested', concat_dims='datanumber')
    return VPxr
    
def read_VPOLA_dates(date_range, expt, ddir=mdir, trial='trial', ext='000', group='VP/VP_GEN_INSITU_REALTIME'):

    files = obtain_files(date_range, expt, OLA='VP', trial=trial, ext=ext, ddir=ddir)
    VPxr = xr.open_mfdataset(files, group=group, combine='nested', concat_dim='datanumber')
    return VPxr
# OTHER QCOLA files should be similar

    
