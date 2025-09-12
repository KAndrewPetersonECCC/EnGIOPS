## I am concerned with
 # How The spread changes with time
 # How the spread changes with lead (but independent) of time
   # Neither requires the full ensemble -- can reduce to 3D+T spread/variance and mean
 # Even with DASK, not sure I can load a full 3D+T+L?  
import sys
import os
#import traceback
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
#from importlib import reload

import xarray as xr
import numpy as np
import datetime

import check_date
import create_dates

mdir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives';
expt='dev-4.0.0.ensembles_CTL'
date_str='2022010500'
dates = create_dates.create_dates(20211020, 20220914,7)
lead=168
lead_str=str(lead).zfill(3)
bile=date_str+'_'+lead_str+'_1d_grid_T.nc'
file=mdir+'/'+expt+'/netcdf.001/outputs/anal/giops+1/oce/'+bile

files=[]
for ens in np.arange(0,20)+1:
    ens_str3 = str(ens).zfill(3)
    ens_str1 = '+'+str(ens)
    file=mdir+'/'+expt+'/netcdf.'+ens_str3+'/outputs/anal/giops'+ens_str1+'/oce/'+bile
    files.append(file)

eset = xr.open_mfdataset(files, combine='nested', concat_dim='ensemble')    

default_ensemble = list((np.arange(20)+1).astype(int)) # 1-20 
def read_expt_ensemble(expt, date, lead, var=None, grid='T', depth=None, freq='1d', ddir=mdir, ensemble=default_ensemble):
    fvar=var
    if ( var == 'T' ): fvar='thetao'
    if ( var == 'S' ): fvar='so'
    if ( var == 'U' ): fvar='uo'
    if ( var == 'V' ): fvar='vo'
    if ( var == 'U' ): grid='U'
    if ( var == 'V' ): grid='V'
    if ( grid == 'T' ): depvar = 'deptht'
    if ( grid == 'U' ): depvar = 'depthu'
    if ( grid == 'V' ): depvar = 'depthv'
    #addD=''
    #if ( twoD ): addD='_2D'
    date_str=check_date.check_date(date, outtype=str, dtlen=10)
    lead_str=str(lead).zfill(3)
    bile=date_str+'_'+lead_str+'_'+freq+'_grid_'+grid+'.nc'
    elist=[]
    for ensm in ensemble:
        file=ddir+'/'+expt+'/netcdf.'+ens_str3+'/outputs/anal/giops'+ens_str1+'/oce/'+bile
        fset=xr.open_dataset(file)
        elist.append(fset)
    eset = xr.concat(elist, dim='ensemble')
    if ( isinstance(var, type(None)) ):
        return(eset)
    else:
        evar = eset[fvar]
        del(eset)
        if ( not isinstance(depth, type(None) ) ):
            if ( depth == 0 ):
                idepth = 0
            else:
                idepth = np.argmin(np.abs(evar[depvar].values - depth))
            #print(idepth, depvar)
            if ( depvar == 'deptht' ): evar = evar.isel(deptht=idepth)
            if ( depvar == 'depthu' ): evar = evar.isel(depthu=idepth)
            if ( depvar == 'depthv' ): evar = evar.isel(depthv=idepth)
            #evar = evar.loc[depvar==idepth]
        return(evar)

def cycle_thru_analdate(expt, dates, lead, var='T', grid='T', depth=0, freq='1d', ddir=mdir, ensemble=default_ensemble, time_dim='time_counter'):
    fvar=var
    ndates = len(dates)
    if ( var == 'T' ): fvar='thetao'
    if ( var == 'S' ): fvar='so'
    if ( var == 'U' ): fvar='uo'
    if ( var == 'V' ): fvar='vo'
    if ( var == 'U' ): grid='U'
    if ( var == 'V' ): grid='V'
    vlist = []
    mlist = []
    for idate, date in enumerate(dates):
        print(date)
        sdate = date - datetime.timedelta(days=7)
        fldarr =  read_expt_ensemble(expt, sdate, lead, depth=depth, var=fvar, grid=grid, freq=freq, ddir=ddir, ensemble=ensemble)       
        fldvar = np.square(fldarr.std(dim='ensemble'))
        fldavg = fldarr.mean(dim='ensemble')
        #vlist.append(fldvar)
        #mlist.append(fldavg)
        if ( idate == 0 ):
            avgvar = fldvar/ndates
            avgmne = fldavg/ndates
        else:
            avgvar = avgvar + fldvar/ndates
            avgmne = avgmne + fldavg/ndates
    #varr = xr.concat(vlist, dim=time_dim).compute()
    #marr = xr.concat(mlist, dim=time_dim).compute()
    return avgvar, avgmne
        

def cycle_thru_leads(expt, dates, leads, var='T', grid='T', depth=0, freq='1d', ddir=mdir, ensemble=default_ensemble, time_dim='time_counter'):
    lvlist = []
    lmlist = []
    for lead in leads:
        marr, varr = cycle_thru_analdate(expt, dates, lead, var=var, depth=depth, grid=grid, freq=freq, ddir=ddir, ensemble=default_ensemble, time_dim='time_counter')
        lvlist.append(varr)
        lmlist.append(mvar)
    lvarr=xr.concat(lvlist, dim='lead'); lvarr['lead'] = lead
    lmarr=xr.concat(lmlist, dim='lead'); lmarr['lead'] = lead
    return lmarr, lvarr
