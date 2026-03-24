import sys
import os
import xarray as xr
import netCDF4 as nc
import numpy as np
import glob
import check_date

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import create_dates

mdir = '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
kdir = '/fs/site5/eccc/cmd/e/kch001/maestro_archives/SAM2v2'
rbdir = '/fs/site5/eccc/cmd/e/rrh002/maestro_archives/'

def change_dir(ddir=mdir):
    if ( ddir == 'SAM2V2' ): ddir=mdir+'/SAM2V2'
    if ( ddir == 'kch001' ): ddir=kdir
    if ( ddir == 'rrh002' ): ddir=rbdir
    if ( ddir[0] == '+' ): ddir=mdir+'/'+ddir[1:]
    return ddir
  
def obtain_files(date_range, expt, OLA='VP', trial='trial', ext='000', ddir=mdir, ens=None):
    ddir=change_dir(ddir)
    enss=''
    if ( not isinstance(ens, type(None)) ):
        if (  isinstance(ens, str) ):
            enss=ens+'/'
        else:
            enss=str(ens).zfill(3)+'/'

    if ( isinstance(date_range, str) ):
        if ( date_range == '*' or date_range.casefold() == 'All'.casefold() ):
            date='????????'
            scan=ddir+'/'+expt+'/SAM2/'+enss+date+'/DIAG/'+trial+'/'+date+ext+'_QCOLA_'+OLA+'_BEST.nc'
            print('ls '+scan)
            files = glob.glob(scan)
        return files
    if ( len(date_range) == 3 ):
        dates=create_dates.create_dates(date_range[0], date_range[1], date_range[2])
    elif ( len(date_range) == 2 ):
        dates=create_dates.create_dates(date_range[0], date_range[1], 7)
    else:
        dates=date_range
        
    if ( isinstance(dates[0], str) ):
        dates_str = dates
    else:
        dates_str = check_date.check_date_list(dates, outtype=str, dtlen=8)
   

    files = []
    for date in dates_str:
        file = ddir+'/'+expt+'/SAM2/'+enss+date+'/DIAG/'+trial+'/'+date+ext+'_QCOLA_'+OLA+'_BEST.nc'
        print('file = ', file)
        if os.path.isfile(file):
            files.append(file)
    
    #print('files = ', files)
    return files

def read_VPOLA(files, group='VP/VP_GEN_INSITU_REALTIME'):

    VPxr = xr.open_mfdataset(files, group=group, combine='nested', concat_dim='datanumber')
    return VPxr
    
def read_VPOLA_dates(date_range, expt, ddir=mdir, trial='trial', ext='000', group='VP/VP_GEN_INSITU_REALTIME', ens=None):

    files = obtain_files(date_range, expt, OLA='VP', trial=trial, ext=ext, ddir=ddir, ens=ens)
    VPxr = xr.open_mfdataset(files, group=group, combine='nested', concat_dim='datanumber')
    return VPxr

def get_TYPE(FLD):
    TYPE=''
    if ( FLD == 'SLA' ): TYPE = 'IS'
    if ( FLD == 'SST' ): TYPE = 'DS'
    if ( FLD == 'VP'): TYPE = 'VP'
    return TYPE
    
def find_group_types(date, expt='global_v1.0.0', primary='SLA', ext='000', ddir=mdir, is_trial=True, ens=None ):
    if ( not isinstance(ens, type(None)) ):
        ens_str = str(ens).zfill(3)+'/'
    else:
        ens_str = ''
    if ( isinstance(date, list) ) :
        all_types = []
        for this_date in date:
            types = find_group_types(this_date, expt=expt, primary=primary, ext=ext, ddir=ddir, is_trial=is_trial )
            for this_type in types:
                if this_type not in all_types:
                    all_types.append(this_type)
        return all_types
    datestr = check_date.check_date(date, dtlen=8)
    TYPE = get_TYPE(primary)
    if ( is_trial ):
        trial = 'trial'
    else:
        trial = 'iau'
    file = ddir+'/'+expt+'/SAM2/'+ens_str+datestr+'/DIAG/'+trial+'/'+datestr+ext+'_QCOLA_'+TYPE+'_BEST.nc'
    with nc.Dataset(file) as DS:
        types=list(DS.groups[primary].groups.keys())
    return types    

def read_VPOLA_ens(date_range, expt, ddir=mdir, trial='trial', ext='000', group='VP/VP_GEN_INSITU_REALTIME', ensemble=list(np.arange(1,21,1))):

    ENS = read_OLS_ENS(date_range, expt, ddir=ddir, trial=trial, ext=ext, group=group, ensemble=ensemble)
    return ENS

def read_OLA_ens(date_range, expt, ddir=mdir, trial='trial', ext='000', group='VP/VP_GEN_INSITU_REALTIME', ensemble=list(np.arange(1,21,1))):

    ENS = []
    OLAA = group.split('/')[0]
    if ( OLAA == 'VP' ): OLA='VP'
    if ( OLAA == 'SLA' ): OLA='IS'
    if ( OLAA == 'SST' ): OLA='DS'
    for ens in ensemble:
        files = obtain_files(date_range, expt, OLA=OLA, trial=trial, ext=ext, ddir=ddir, ens=ens)
        VPxr = xr.open_mfdataset(files, group=group, combine='nested', concat_dim='datanumber')
        VPxr['ensemble'] = ens + 0*VPxr['datanumber']
        #print(VPxr['eqv_temperature'].shape)
        ENS.append(VPxr)
    #VPens = xr.concat(ENS, dim='edim')    
    return ENS

# OTHER QCOLA files should be similar

def add_square_error(VPA, vars=['mis_temperature', 'mis_salinity'], varo=['sqe_temperature', 'sqe_salinity']):
    nvars = len(vars)
    for ii in range(nvars):
        VPA[varo[ii]] = np.square(VPA[vars[ii]])
    return VPA

def calc_EM_add_variance(VPE, vars=['mis_temperature', 'mis_salinity'], varo=['var_temperature', 'var_salinity']):
    VPS = VPE.std(dim='edim')
    VPM = VPE.mean(dim='edim')
    nvars = len(vars)
    for ii in range(nvars):
        VPM[varo[ii]] = np.square(VPS[vars[ii]])
    return VPM
