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

import multiprocessing as mp
import itertools
from functools import partial
import time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import check_date
import create_dates
import read_grid_xr

num_cpus = len(os.sched_getaffinity(0))
max_cpus = 8

#e1t = np.squeeze(read_grid_xr.read_mesh_var('e1t')).load()
#e2t = np.squeeze(read_grid_xr.read_mesh_var('e2t')).load()
#e3t = np.squeeze(read_grid_xr.read_mesh_var('e3t_0')).load()
#garea=e1t*e2t

nav_lat_mesh = read_grid_xr.read_mesh_var('nav_lat').load()
nav_lon_mesh = read_grid_xr.read_mesh_var('nav_lon').load()
nav_lev_mesh = read_grid_xr.read_mesh_var('nav_lev').load()

krange = np.where(nav_lev_mesh < 1000.0)[0]

mdir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives';

default_experiment = 'dev-4.0.0.ensembles_CTL'
default_expt='dev-4.0.0.ensembles_CTL'
default_ensemble = list((np.arange(20)+1).astype(int)) # 1-20 
default_leads = np.arange(24,169,24)
default_dates = create_dates.create_dates(20220105,20220131,7)
defull_dates = create_dates.create_dates(20211013, 20220921,7)

def read_mask(grid):
    if ( grid == 'T' ): sgrid='t'
    if ( grid == 'U' ): sgrid='u'
    if ( grid == 'V' ): sgrid='v'
    mask = np.squeeze(read_grid_xr.read_mesh_var(sgrid+'mask')).load()
    mask = mask.isel(z=krange).compute()
    e1 = np.squeeze(read_grid_xr.read_mesh_var('e1'+sgrid)).load()
    e2 = np.squeeze(read_grid_xr.read_mesh_var('e2'+sgrid)).load()
    garea = e1*e2
    return mask, garea
    
maskT, gareaT = read_mask('T')
    
def read_expt_ensemble(expt, date, lead, var=None, depth=None, freq='1d', ddir=mdir, ensemble=default_ensemble):
    fldvar, grid, depvar = find_var_grid(var)
    date_str=check_date.check_date(date, outtype=str, dtlen=10)
    lead_str=str(lead).zfill(3)
    bile=date_str+'_'+lead_str+'_'+freq+'_grid_'+grid+'.nc'
    elist=[]
    for ensm in ensemble:
        ens_str3 = str(ensm).zfill(3)
        ens_str1 = '+'+str(ensm)
        file=ddir+'/'+expt+'/netcdf.'+ens_str3+'/outputs/anal/giops'+ens_str1+'/oce/'+bile
        with xr.open_dataset(file) as fset:
           timevar=list(fset.dims)[0]
           #fset=xr.open_dataset(file)
           if ( isinstance(var, type(None)) ):
               elist.append(fset)
           else:
               fvar = fset[fldvar]
               if ( not isinstance(depth, type(None) ) ):
                   if ( depth == 0 ):
                       idepth = 0
                   else:
                        idepth = np.argmin(np.abs(evar[depvar].values - depth))
                   if ( depvar == 'deptht' ): fvar = fvar.isel(deptht=idepth)
                   if ( depvar == 'depthu' ): fvar = fvar.isel(depthu=idepth)
                   if ( depvar == 'depthv' ): fvar = fvar.isel(depthv=idepth)
               else:
                   if ( depvar == 'deptht' ): fvar = fvar.isel(deptht=krange)
                   if ( depvar == 'depthu' ): fvar = fvar.isel(depthu=krange)
                   if ( depvar == 'depthv' ): fvar = fvar.isel(depthv=krange)
                   #print('SHAPE', fvar.shape)
               elist.append(fvar)    
    eset = xr.concat(elist, dim='ensemble')
    return eset.compute(), timevar, depvar

def cycle_thru_analdate(expt, dates, lead, var='T', grid='T', depth=0, freq='1d', ddir=mdir, ensemble=default_ensemble, time_dim='time_counter'):
    ndates = len(dates)
    vlist = []
    mlist = []
    for idate, date in enumerate(dates):
        print(date)
        sdate = date - datetime.timedelta(days=7)
        fldarr, timevar, depvar =  read_expt_ensemble(expt, sdate, lead, depth=depth, var=var, freq=freq, ddir=ddir, ensemble=ensemble)       
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

def calc_global_average(fldarr, mask, area, timevar='time_counter', depvar='deptht'):
    print("TYPERS", type(fldarr), type(mask), type(area))
    SUMFLD = np.nansum(fldarr.data * mask.data * area.data, axis=(-2, -1))
    SUMARA = np.nansum(mask*area, axis=(-2, -1))
    #print(SUMFLD.shape, SUMARA.shape)
    fldglb = SUMFLD/SUMARA
    #print(fldglb.shape)
    flaglb = xr.DataArray(fldglb, dims=fldarr.dims[0:-2])
    flaglb[depvar] = fldarr[depvar].compute()
    flaglb[timevar] = fldarr[timevar].compute()
    return flaglb.compute()

def do_global_average(expt, date, lead, var='T', depth=None, freq='1d', ddir=mdir, ensemble=default_ensemble):
    fldarr, timevar, depvar =  read_expt_ensemble(expt, date, lead, depth=depth, var=var, freq=freq, ddir=ddir, ensemble=ensemble)
    fldvar = np.square(fldarr.std(dim='ensemble'))
    fldavg = fldarr.mean(dim='ensemble')
    del fldarr
    __, grid, __ = find_var_grid(var)
    gmask, ggarea = read_mask(grid)
    flaglv = np.sqrt(calc_global_average(fldvar, gmask, ggarea, timevar=timevar, depvar=depvar))
    flaglm = calc_global_average(fldavg, gmask, ggarea, timevar=timevar, depvar=depvar)
    del fldvar, fldavg
    return flaglv, flaglm

def do_global_average_tuple(date_lead, expt=default_experiment,  var='T', depth=None, freq='1d', ddir=mdir, ensemble=default_ensemble):
    date=date_lead[0]
    lead=date_lead[1]
    flaglv, flaglm = do_global_average(expt, date, lead, var=var, depth=None, freq='1d', ddir=mdir, ensemble=default_ensemble) 
    return flaglv, flaglm
    
def cycle_thru_leads_date(expt, dates, leads, 
                          var='T', depth=None, freq='1d', mp_loop=False, mp_type=0,
                          ddir=mdir, ensemble=default_ensemble, time_dim='time_counter', anal_date=False):

    leadv = []
    leadm = []   
    time0 = time.time()
    if ( not mp_loop): 
        for date in dates: 
            if anal_date:
                sdate = date - datetime.timedelta(days=7)
            else:
                sdate = date
            for lead in leads:
                print(sdate, lead)
                flaglv, flaglm = do_global_average(expt, sdate, lead, var=var, depth=depth, freq=freq, ddir=mdir, ensemble=ensemble)
                leadv.append(flaglv)
                leadm.append(flaglm)
    else:
        iizip = []
        ijzip = []
        for date in dates: 
            if anal_date:
                sdate = date - datetime.timedelta(days=7)
            else:
                sdate = date
            for lead in leads:
                iizip.append((sdate, lead))
                ijzip.append((expt, sdate, lead))
        
        nproc = np.min([num_cpus, len(iizip), max_cpus])
        print('NPROC ', nproc, num_cpus, len(iizip), max_cpus)
        with mp.Pool(nproc) as MPPool:
          if ( mp_type == 0  ):
            partial_func = partial(do_global_average, depth=depth, var=var, freq=freq, ddir=mdir, ensemble=ensemble)
            MP_LIST = MPPool.starmap(partial_func, ijzip)
          else:  
            partial_func = partial(do_global_average_tuple, expt=expt, depth=depth, var=var, freq=freq, ddir=mdir, ensemble=ensemble)
            MP_LIST = MPPool.imap(partial_func, iizip)
        for return_list in MP_LIST:
            flaglv, flaglm = return_list
            leadv.append(flaglv)
            leadm.append(flaglm)
    glbvar=xr.concat(leadv, dim=time_dim)
    glbmne=xr.concat(leadm, dim=time_dim)
    #glbvar.dims
    #glbvar.coords
    #glbvar[time_dim]
    print('GLOBAL CALC TIME ', time.time()-time0)
    fvar, grid, depvar = find_var_grid(var)
    plot_hovmuller(glbvar, time_var=time_dim, depth_var=depvar, outfile='E2/'+var+'var_hov.png')
    plot_hovmuller(glbmne, time_var=time_dim, depth_var=depvar, outfile='E2/'+var+'ave_hov.png')
    return glbvar, glbmne

def find_var_grid(var):
    grid='T'
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
    return fvar, grid, depvar

def plot_hovmuller(glbvar, time_var='time_counter', depth_var='deptht', outfile='plot.png'):
    myFmt = mdates.DateFormatter('%d/%m')
    times = glbvar[time_var]
    depth = glbvar[depth_var]
    fig, axe = plt.subplots()
    
    mesh=axe.pcolormesh(times, depth, np.transpose(glbvar.data))
    
    axe.set_xlabel('date')
    axe.set_ylabel('depth (m)')
    axe.xaxis.set_major_formatter(myFmt)
    axe.set_ylim(0,500)
    axe.invert_yaxis()
    axe.tick_params(axis='x', labelrotation=45)    
    cbar_fig=fig.colorbar(mesh, format='%.3f',orientation='horizontal')
    fig.savefig(outfile)
    
    return
