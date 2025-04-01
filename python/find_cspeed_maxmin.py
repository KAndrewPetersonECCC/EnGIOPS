#from importlib import reload
import sys
import os
import psutil
import time
import glob

import numpy as np
import numbers
import datetime
#import pytz
from scipy import signal

import multiprocessing
import itertools
from functools import partial
from multiprocessing import active_children

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import read_dia
import read_grid
import check_date
import cplot

import find_geps_fcst
import stfd
import soundspeed
import read_ensemble_forecast
import read_EN4
import find_value_at_point
import datadatefile
import rank_histogram
import write_nc_grid
import matplotlib.cm as cm
import copy

cmap_full='YlOrRd'
cmap_anom='RdYlBu_r'
cmap_full='gist_stern_r'
cmap_anom='seismic'
cmap_anom = copy.copy(cm.seismic)
cmap_anom.set_bad('g', 1.0)
cmap_full = copy.copy(cm.gist_stern_r)
cmap_full.set_bad('g', 1.0)

eg_file='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_320_GU/SAM2/20201009/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020100900.nc'
depth_default =  read_dia.read_sam2_levels(eg_file)

hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

lonn, latn, orca_area = read_grid.read_coord()

NCPUS = len(os.sched_getaffinity(0))
def calc_sound_speed_globe(TFLD, SFLD, depth):
    if ( isinstance(depth, list) ): depth=np.array(depth)
    if ( TFLD.ndim == 3 ):
        depth3D = np.broadcast_to(depth[:, np.newaxis, np.newaxis], TFLD.shape)
    if ( TFLD.ndim == 4 ):
        depth3D = np.broadcast_to(depth[np.newaxis, :, np.newaxis, np.newaxis], TFLD.shape)
    CFLD = soundspeed.sound_speed(depth3D, SFLD, TFLD)
    return CFLD

def calc_sound_speed_ensemble(eTFLD, eSFLD, depth, mp_ensemble=False):
    nproc = np.min([NCPUS, len(eTFLD)])
    zip_args = list( zip(eTFLD, eSFLD, itertools.repeat(depth)) )
    if ( mp_ensemble ):
        Epool = multiprocessing.Pool(nproc)
        eCFLD = Epool.starmap(partial(calc_sound_speed_globe), zip_args)
        Epool.close()
        Epool.join()
        #children = active_children()
        #print(f'Active children: {len(children)}')
    else:
        eCFLD=[]
        for args in zip_args:
            CFLD = calc_sound_speed_globe(*args)
            eCFLD.append(CFLD)
    return eCFLD
    
    IVAL = np.where(TFLD[0,:,:].mask == False )
    CFLD = 0.0*TFLD.copy()
    for ii in range(len(IVAL[0])):
        Sprof = SFLD[:, IVAL[0][ii], IVAL[1][ii]]
        Tprof = TFLD[:, IVAL[0][ii], IVAL[1][ii]]
        Cprof = soundspeed.sound_speed(depth, Sprof, Tprof)
        CFLD[:, IVAL[0][ii], IVAL[1][ii]] = Cprof
    return CFLD

def find_mins_depth(cprof, depth, mindepth, maxdepth):
    mins, __ = signal.find_peaks(-1*cprof, prominence=0.5)
    DEPTHS=depth[mins]
    TorF = (np.any( (DEPTHS > mindepth ) & ( DEPTHS < maxdepth) ))
    MINdepth = 9999
    if ( len(DEPTHS) > 0 ):
          MINdepth = np.min(DEPTHS)
    return TorF, MINdepth   

# MAKE SURE THIS DIDNT BREAK MODEL CALCULATION    
def find_mins(cprof, depth=depth_default, mindepth=10.0, maxdepth=100.0):
    TorF, MINdepth = find_mins_depth(cprof, depth, mindepth, maxdepth)
    return TorF, MINdepth   

def find_mins_obs(COBS, DEP, mindepth=10.0, maxdepth=100.0, mp=False):
    nobs, nprof = COBS.shape
    CLST = []
    DLST = []
    for iobs in range(nobs):
        CLST.append(COBS[iobs,:])
        DLST.append(DEP[iobs,:])
    TorF_list = []
    RESULTS = []
    if ( mp ):
        nproc = np.min([NCPUS, nobs])
        Opool = multiprocessing.Pool(nproc)
        IZIP = list(zip(CLST, DLST, itertools.repeat(mindepth), itertools.repeat(maxdepth)))
        RESULTS = Opool.starmap(find_mins_depth, IZIP)
        Opool.close()
        Opool.join()
    else:
        for iobs in range(nobs):
            TorF, MINdepth = find_mins_depth(CLST[iobs], DLST[iobs], mindepth, maxdepth)
            RESULTS.append([TorF, MINdepth])
    for result in RESULTS:
        TorF_list.append(result[0])
    return TorF_list
            
    
def find_mins_arr(CFLD, depth=depth_default, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=True, byxy=False):
    print(CFLD.shape)
    nz, nx, ny = CFLD.shape
    smask = CFLD.mask[0,:,:]
    ISEA = np.where(smask == False)
    npts=len(ISEA[0])
    TorF = np.zeros((nx,ny)).astype(bool)
    MDep = np.zeros((nx,ny))+9999
    if ( bySea ):
        nproc = np.min([NCPUS, npts])
        CPROS_LIST = []
        for ipt in range(npts):
          CPROS_LIST.append(CFLD[:, ISEA[0][ipt], ISEA[1][ipt]])
        if ( mp_depth == True ):
            Epool = multiprocessing.Pool(nproc)
            RESULTS = Epool.map(partial(find_mins, depth=depth, mindepth=mindepth, maxdepth=maxdepth), CPROS_LIST)
            Epool.close()
            Epool.join()
        else:
            RESULTS = []
            for CPROS in CPROS_LIST:
                RESULTS.append(find_mins(CPROS, depth=depth, mindepth=mindepth, maxdepth=maxdepth))
        for ipt, RESULT in enumerate(RESULTS):
            TorF[ISEA[0][ipt],ISEA[1][ipt]] = RESULT[0]
            MDep[ISEA[0][ipt],ISEA[1][ipt]] = RESULT[1]
    elif ( byxy) :
        nproc = np.min([NCPUS, nx*ny])
        CPROS_LIST = []
        for ix in range(nx):
             for iy in range(ny):
                CPROS=CFLD[:,ix,iy]
                CPROS_LIST.append(CPROS)
        if ( mp_depth == True ):
            Epool = multiprocessing.Pool(nproc)
            RESULTS = Epool.map(partial(find_mins, depth=depth, mindepth=mindepth, maxdepth=maxdepth), CPROS_LIST)  # BUT IS THIS ORDERED in X/Y still?
            Epool.close()
            Epool.join()
        else:
                RESULTS = []
                for CPROS in CPROS_LIST:
                    RESULTS.append(find_mins(CPROS, depth=depth, mindepth=mindepth, maxdepth=maxdepth))
        ir=0
        for ix in range(nx):
            for iy in range(ny):
                RESULT = RESULTS[ir]
                TorF[ix, iy] = RESULT[0]
                MDep[ix, iy] = RESULT[1]
                ir=ir+1
    else:
        nproc = np.min([NCPUS, ny])
        if ( mp_depth == True ): print("NOT A GOOD METHOD: USE bySea OR byxy")
        for ix in range(nx):
            CPROS_LIST = []
            for iy in range(ny):
                CPROS=CFLD[:,ix,iy]
                CPROS_LIST.append(CPROS)
            if ( mp_depth == True ):
                #print(ix)
                time0=time.time()
                Epool = multiprocessing.Pool(nproc)
                RESULTS = Epool.map(partial(find_mins, depth=depth, mindepth=mindepth, maxdepth=maxdepth), CPROS_LIST)  # BUT IS THIS ORDERED in Y still?
                Epool.close()
                Epool.join()
                print(ix, time.time()-time0, flush=True)  # METHOD MAY HANG?
            else:
                RESULTS = []
                for CPROS in CPROS_LIST:
                    RESULTS.append(find_mins(CPROS, depth=depth, mindepth=mindepth, maxdepth=maxdepth))
            for iy, RESULT in enumerate(RESULTS):
                TorF[ix, iy] = RESULT[0]
                MDep[ix, iy] = RESULT[1]
    return TorF, MDep
          
def find_mins_ens(ECFLD, depth=depth_default, mindepth=10.0, maxdepth=100.0, mp_ensemble=True, mp_depth=False, bySea=True, byxy=False, GIOPS=True):
    mp_usedepth = mp_depth
    nproc = np.min([NCPUS, len(ECFLD)])
    if ( mp_ensemble ):  mp_usedepth=False

    ETorF = []
    EMDep = []
    if ( mp_ensemble ):
        Epool = multiprocessing.Pool(nproc)
        RESUT = Epool.map(partial(find_mins_arr, depth=depth, mindepth=mindepth, maxdepth=maxdepth, mp_depth=mp_usedepth, bySea=bySea, byxy=byxy), ECFLD)
        Epool.close()
        Epool.join()
        for RESUL in RESUT:
            TorF, MDep = RESUL
            ETorF.append(TorF)
            EMDep.append(MDep)
    else:
        for ie, CFLD in enumerate(ECFLD):
            TorF, MDep = find_mins_arr(CFLD, depth=depth, mindepth=mindepth, maxdepth=maxdepth, mp_depth=mp_usedepth, bySea=bySea, byxy=byxy)
            ETorF.append(TorF)
            EMDep.append(MDep)
    PDuctA = sum( [TorF.astype(float) for TorF in ETorF] )/len(ETorF)
    PVar, PDuct = read_dia.ensemble_var(ETorF)
    PVar_masked = add_mask(PVar, GIOPS=GIOPS)
    PDuct_masked = add_mask(PDuct, GIOPS=GIOPS)
    print( np.all(PDuctA == PDuct) )
    return ETorF, EMDep, PDuct_masked, PVar_masked
    
def find_sound_channels(CFLD, depth=depth_default, mp=False):
    if ( isinstance(CFLD, list) ) :
      if ( mp ):
        nproc = np.min([NCPUS, len(CFLD)])
        Epool = multiprocessing.Pool(nproc)
        SOUND_RESULT = Epool.map(partial(find_sound_channels, depth=depth, mp=False), CFLD)
        Epool.close()
        Epool.join()
      else:
        SOUND_RESULT = []
        for iCFLD in CFLD:
            SOUND_RESULT.append(find_sound_channels(iCFLD))
      SOUND_CHANNEL = []
      SOUND_BARRIER = []
      for i_RESULT in SOUND_RESULT:
        SOUND_CHANNEL.append(i_RESULT[0])
        SOUND_BARRIER.append(i_RESULT[1])
    else:
        IMIN = np.argmin(CFLD, axis=0)
        SOUND_CHANNEL = depth[IMIN]
        IMAX = np.argmax(CFLD, axis=0)
        SOUND_BARRIER = depth[IMAX]
    return SOUND_CHANNEL, SOUND_BARRIER

def find_nearest_analysis(date):
    #find days to next gd analysis, which are produced on Wednesday (2 for Monday=0)
    anal_diff = ( 2-date.weekday() ) % 7
    anal_date = date + datetime.timedelta(days=anal_diff)
    return anal_date, anal_diff

def close_match_of_date(times, date, max_dt=3600.):
    DT = [time-date for time in times]
    TF = [ (abs(dt).total_seconds() < max_dt) for dt in DT]
    itime = TF.index(True)
    return itime

def read_cspeed_fcst(date, lhr, expt='OPER', ddir=mir5, exec=True, GIOPS=True):
    ETFLD = []
    ESFLD = []
    for ie in range(21):
        if ( expt == 'OP' ):
            file=find_geps_fcst.find_geps_ocn_fcst(date, lhr, ie, sys='OP', execute=exec, only_this_ens=False)
        if ( expt == 'PS' ):
            file=find_geps_fcst.find_geps_ocn_fcst(date, lhr, ie, sys='PS', execute=exec, only_this_ens=False)
        if ( ie == 0 ) : lone, late = stfd.read_latlon(file)
        depthT, T_3D = stfd.read_fstd_multi_lev(file, 'TM', vfreq=24, typvar='P@')
        depthS, S_3D = stfd.read_fstd_multi_lev(file, 'SALW', vfreq=24, typvar='P@')
        ETFLD.append(soundspeed.Kelvin_to_Celsius(T_3D))
        ESFLD.append(S_3D)
    depthT = np.array(depthT)
    depthS = np.array(depthS)
    ETFLD = add_mask(ETFLD, GIOPS=GIOPS)
    ESFLD = add_mask(ESFLD, GIOPS=GIOPS)
    ECFLD = calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True)     
    return depthT, lone, late, ECFLD, ETFLD, ESFLD
        
                  
def read_cspeed_date(date, expt='GIOPS_T', ddir=mir5, anal=True, ensembles=[], verbose=False, GIOPS=True):
    
    if ( GIOPS ): GIOPS_PRE='ORCA025-CMC'
    if ( not GIOPS ): GIOPS_PRE='Creg12-CMC'

    if ( verbose ):
        print('ENSEMBLES in read_cspeed_date at start = ', ensembles) 
    
    date=check_date.check_date(date, outtype=datetime.datetime)
    date=check_date.add_utc(date)

    if ( ensembles == 'c' or ensembles == 'C' or ensembles == 'l' or ensembles == 'L' ):
        #OUTPUTS depthT, lone, late, ECFLD, ETFLD, ESFLD
        if ( ensembles == 'c' or ensembles == 'C' ):
            frst=datetime.datetime(2019, 7, 3) + datetime.timedelta(days=21); frst=check_date.add_utc(frst)
            last=datetime.datetime(2023, 5, 24) - datetime.timedelta(days=21); last=check_date.add_utc(last)
            fyrs=2019
            lyrs=2023
            if ( date.timetuple().tm_yday < frst.timetuple().tm_yday ): fyrs=2020
            if ( date.timetuple().tm_yday < last.timetuple().tm_yday ): lyrs=2024
            cyrs=list(range(fyrs, lyrs, 1))
        else:
            date_str = check_date.check_date(date, outtype=str)
            cyrs = [ int(date_str[0:4]) ]
        print(cyrs)    
        ECFLD=[]
        ETFLD=[]
        ESFLD=[]
        for year in cyrs:
            date_str=check_date.check_date(date, outtype=str)
            year_str=str(year)
            date_new=year_str+date_str[4:]
            print(date_new)
            date_new = check_date.check_date(date_new, outtype=datetime.datetime)
            for lag in [-14, -7, 0, 7, 14]:
                date_in = date_new + datetime.timedelta(days=lag)
                print(date_in)
                depthT, lone, late, CFLD, TFLD, SFLD = read_cspeed_date(date_in, expt=expt, ddir=ddir, anal=anal, ensembles='d', verbose=verbose, GIOPS=GIOPS)
                ECFLD.append(CFLD[0])
                ETFLD.append(TFLD[0])
                ESFLD.append(SFLD[0])
        return depthT, lone, late, ECFLD, ETFLD, ESFLD
        
    #find days to next gd analysis
    anal_date, anal_diff = find_nearest_analysis(date)
    if ( verbose ):
      print(date, anal_date, anal_diff)
      print('MEMORY = ', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    late = None
    lone = None
    depthT = None
    ETFLD = None
    ESFLD = None
    ECFLD = None
    
    if ( anal ):   # ASSUME 1d IAU.  only anal_date available.
        if ( anal_diff == 0 ):
            if ( verbose ):
              print('ENSEMBLES in read_cspeed_date with anal = ', ensembles) 
            file_pre=GIOPS_PRE+'-ANAL_1d_'
            time, depthT, lone, late, ETFLD_big = read_dia.read_ensemble_plus_depthandtime(ddir, expt, date, fld='T', time_fld='time_instant', file_pre=file_pre, ensembles=ensembles)
            lone, late, ESFLD_big = read_dia.read_ensemble(ddir, expt, date, fld='S', file_pre='ORCA025-CMC-ANAL_1d_',ensembles=ensembles)
            ETFLD = [ TFLD[0].copy() for TFLD in ETFLD_big]     
            del(ETFLD_big)
            ESFLD = [ SFLD[0].copy() for SFLD in ESFLD_big]
            del(ESFLD_big)
        else:
           print('anal = ', anal, ' but anal_diff = ', anal_diff)
           depthT, lone, late, ECFLD, ETFLD, ESFLD = None, None, None, None, None, None
    else:
        if ( verbose ): print('ENSEMBLES in read_cspeed_date with trial = ', ensembles) 
        if ( GIOPS ):
            file_pre=GIOPS_PRE+'-TRIAL_1d_'
            time, depthT, lone, late, ETFLD_big = read_dia.read_ensemble_plus_depthandtime(ddir, expt, anal_date, fld='T', time_fld='time_instant', file_pre=file_pre, ensembles=ensembles)
            lone, late, ESFLD_big = read_dia.read_ensemble(ddir, expt, anal_date, fld='S', file_pre=file_pre,ensembles=ensembles)
            for iens, TFLD in enumerate(ETFLD_big):
                nt, nz, nz, ny = TFLD.shape
                if ( nt != 7 ):  print('Member Truncated: ', iens, anal_date)
            itime = close_match_of_date(time, date)
            ETFLD = [ TFLD[itime].copy() for TFLD in ETFLD_big]
            del(ETFLD_big)
            ESFLD = [ SFLD[itime].copy() for SFLD in ESFLD_big]
            del(ESFLD_big)
        elif ( not GIOPS ):
            file_pre=GIOPS_PRE+'-TRIAL_1d_'
            ## THIS IS CONFUSING!!!
            ## date is instanteous date at end of observing period (i.e. 0Z the next day)  -- adate in previous instances (adate = date + 1)
            ##   But date in file stamp of RIOPS files is mid-day of day in question (so adate -1)
            fdate = date - datetime.timedelta(hours=12)
            time, depthT, lone, late, ETFLD_big = read_dia.read_ensemble_plus_depthandtime(ddir, expt, fdate, fld='T', time_fld='time_instant', file_pre=file_pre, ensembles=ensembles, date_anal=anal_date)
            lone, late, ESFLD_big = read_dia.read_ensemble(ddir, expt, date, fld='S', file_pre=file_pre, ensembles=ensembles, date_anal=anal_date)
            ETFLD = [ TFLD[0].copy() for TFLD in ETFLD_big]
            ESFLD = [ SFLD[0].copy() for SFLD in ESFLD_big]
            del(ETFLD_big, ESFLD_big)
    if ( not isinstance(ETFLD, type(None)) ): 
        print('Adding Mask')
        print('MEMORY = ', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        ETFLD = add_mask(ETFLD, GIOPS=GIOPS)
        ESFLD = add_mask(ESFLD, GIOPS=GIOPS)
        if ( verbose ):
          print('Begin Calculate C Speed')
          print('MEMORY = ', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        ECFLD = calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True)
    if ( verbose ):
      print('Finish Calculate C Speed')
      print('MEMORY = ', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    return depthT, lone, late, ECFLD, ETFLD, ESFLD

def add_mask(FLD, mask_var='tmask', mp=False, GIOPS=True):
    if ( GIOPS ):
        tmask = np.squeeze(read_grid.read_mask(var=mask_var))
    else:
        tmask = np.squeeze(read_grid.read_riops_mask(var=mask_var))
    if ( isinstance(FLD, list) ):
        if ( mp ):   #  NOTE:  Not actually faster!
            nproc = np.min([NCPUS, len(FLD)])
            Epool = multiprocessing.Pool(nproc)
            MFLD = Epool.map(partial(add_mask, mask_var=mask_var, GIOPS=GIOPS), FLD)
            Epool.close()
            Epool.join()
        else:
            MFLD=[]
            for mFLD in FLD:
                MFLD.append(add_mask(mFLD, mask_var=mask_var, GIOPS=GIOPS))
    elif ( FLD.ndim == 2 ):
        MFLD = np.ma.array(FLD, mask=1-tmask[0,:,:])
    elif ( FLD.ndim == 3 ):
        MFLD = np.ma.array(FLD, mask=1-tmask)
    elif ( FLD.ndim == 4 ):
        mask4 = np.broadcast_to(tmask[np.newaxis, :, :, :], FLD.shape)    # extra time/ensemble index
        MFLD = np.ma.array(FLD, mask=1-mask4)
    elif ( FLD.ndim == 5 ):
        mask5 = np.broadcast_to(tmask[np.newaxis, np.newaxis, :, :, :], FLD.shape)  # extra ensemble+time index
        MFLD = np.ma.array(FLD, mask=1-mask5)
    else:
        MFLD=None
    return MFLD

def find_ducts_for_date(date, anal=False, expt='GIOPS_T', mindepth=10.0, maxdepth=100.0, ddir=mir5, ensembles=[], GIOPS=True):
    print('EMSEMBLES', ensembles, type(ensembles))
    date_str=check_date.check_date(date)
    date=check_date.check_date(date, outtype=datetime.datetime)
    date=check_date.add_utc(date)
    
    if ( anal ):
        anal_date, anal_diff = find_nearest_analysis(date)
        if ( anal_diff != 0 ): 
            print("SHOULD NOT BE HERE")
            return
    depthT, lone, late, ECFLD, ETFLD, ESFLD = read_cspeed_date(date, expt=expt, ddir=ddir, anal=anal, ensembles=ensembles, GIOPS=GIOPS)
    del(ETFLD, ESFLD)   # unless decide they are needed
    if ( not isinstance(depthT, type(None) ) ):
        ETorF, EMDep, PDuct, PVar = find_mins_ens (ECFLD, depth=depthT, mindepth=mindepth, maxdepth=maxdepth, mp_depth=False, bySea=True, mp_ensemble=True, GIOPS=GIOPS)
    else:
        ETorF, EMDep, PDuct, PVar = None, None, None, None
    return ETorF, EMDep, PDuct, PVar

def do_ducts_for_date(date, anal=False, expt='GIOPS_T', mindepth=10.0, maxdepth=100.0, ddir=mir5, pdir='GIOPS_TC',ensembles=[], GIOPS=True):
    date_str=check_date.check_date(date)
    date=check_date.check_date(date, outtype=datetime.datetime)
    date=check_date.add_utc(date)
    
    if ( anal ):
        anal_date, anal_diff = find_nearest_analysis(date)
        if ( anal_diff != 0 ): 
            print("SHOULD NOT BE HERE")
            return

    ETorF, EMDep, PDuct, PVar = find_ducts_for_date(date, anal=anal, expt=expt, mindepth=mindepth, maxdepth=maxdepth, ddir=ddir, ensembles=ensembles, GIOPS=GIOPS)
    del(ETorF, EMDep, PVar)
    AN='T'
    if ( anal ): AN='A'
    outfile=pdir+'/'+'Pduct_'+date_str+'.'+AN
    title='Probability of shallow duct '+date_str
    print('SHAPE', lone.shape, late.shape, PDuct.shape)
    cmap='seismic'
    cmap='RdYlBu_r'
    NA_REG =[-90, 15, 30, 65] 
    cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'.png', project='PlateCarree', obar='horizontal', cmap=cmap, make_global=True, addmask=True)
    cplot.pcolormesh(lone, late, PDuct, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap=cmap)
    cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap=cmap, addmask=True)
    #cplot.pcolormesh(lone, late, PDuct, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), outfile=outfile+'.png', project='PlateCarree', obar='horizontal', cmap=cmap, title=title, make_global=True)
    #cplot.pcolormesh(lone, late, PDuct, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), outfile=outfile+'_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap=cmap)
    return

def do_ducts_for_cycle(this_date, expt='GIOPS_T', mindepth=10.0, maxdepth=100.0, ddir=mir5, pdir='GIOPS_TC', ensembles=[], GIOPS=True):
    this_date=check_date.check_date(this_date, outtype=datetime.datetime)
    this_date=check_date.add_utc(this_date)
    anal_date, anal_diff = find_nearest_analysis(this_date)
    if ( anal_diff != 0 ):
        print('Not an analysis cycle date', date)
        return
    for idate in range(7):
       date = this_date - datetime.timedelta(days=idate) 
       print(date, 'expt = ', expt, 'mindepth =', mindepth, 'maxdepth = ', maxdepth, 'ddir = ', ddir, 'pdir = ', pdir)
       do_ducts_for_date(date, anal=False, expt=expt, mindepth=mindepth, maxdepth=maxdepth, ddir=ddir, pdir=pdir, ensembles=ensembles, GIOPS=GIOPS)
       if ( idate == 0 ):
           do_ducts_for_date(date, anal=True, expt=expt, mindepth=mindepth, maxdepth=maxdepth, ddir=ddir, pdir=pdir, ensembles=ensembles)
    return

 
def do_ducts_for_fcst(date, lhr, expt='OPER', mindepth=10.0, maxdepth=10.0, ddir=mir5, pdir='GEPS_SC'):    
    date_str=check_date.check_date(date, dtlen=10)
    lead_str=str(lhr).zfill(3)
    date=check_date.check_date(date, outtype=datetime.datetime)
    date=check_date.add_utc(date)
    
    depthT, lone, late, ECFLD, ETFLD, ESFLD = read_cspeed_fcst(date, lhr, expt=expt, ddir=ddir, exec=True)
    del(ETFLD, ESFLD)   # unless decide they are needed
    ETorF, EMDep, PDuct, PVar = find_mins_ens (ECFLD, depth=depthT, mindepth=mindepth, maxdepth=maxdepth, mp_depth=False, bySea=True, mp_ensemble=True, GIOPS=True)
    print('PDuct', np.max(PDuct))
    del(ETorF, EMDep, PVar)
    outfile=pdir+'/'+'Pduct_'+date_str+'_'+lead_str
    title='Probability of shallow duct '+date_str+' lead '+lead_str
    #print('SHAPE', lone.shape, late.shape, PDuct.shape)
    cmap='seismic'
    cmap='RdYlBu_r'
    NA_REG =[-90, 15, 30, 65] 
    cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), outfile=outfile+'.sp.png', project='PlateCarree', obar='horizontal', cmap=cmap, title=title, make_global=True, addmask=True)
    cplot.pcolormesh(lone, late, PDuct, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), outfile=outfile+'_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap=cmap)
    cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), outfile=outfile+'_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap=cmap, addmask=True)
    return

def do_ducts_for_fcstdate(date, lds=range(1,33,1), expt='E1Y25EP1', mindepth=10.0, maxdepth=100.0, ddir=hir6, pdir='CSPEED/GENERIC', ensembles=[]):
    if ( isinstance(lds, numbers.Number) ): lds=[lds]
    date_str=check_date.check_date(date)
    date=check_date.check_date(date, outtype=datetime.datetime)
    date=check_date.add_utc(date)

    for lday in lds:    
        lhr = lday*24
        fcst_date=date+datetime.timedelta(days=lday)
        fcst_date_str=check_date.check_date(fcst_date)
        lead_str=str(lday).zfill(2)
        lhrs_str=str(lhr).zfill(3)
        depthT, lone, late, ECFLD, ETFLD, ESFLD = read_ensemble_forecast.get_ensemble_cspeed(expt, date, lhr, ddir=ddir)
        del(ETFLD, ESFLD)   # unless decide they are needed
        ETorF, EMDep, PDuct, PVar = find_mins_ens (ECFLD, depth=depthT, mindepth=mindepth, maxdepth=maxdepth, mp_depth=False, bySea=True, mp_ensemble=True, GIOPS=True)
        del(ETorF, EMDep, PVar)
        outfile=pdir+'/'+'Pduct_'+date_str+'_'+lhrs_str
        title='Probability of shallow duct valid for '+fcst_date_str+' at lead '+lead_str+' day from date '+date_str
        cmap='seismic'
        cmap='RdYlBu_r'
        NA_REG =[-90, 15, 30, 65] 
        cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'.png', project='PlateCarree', obar='horizontal', cmap=cmap, make_global=True, addmask=True)
        cplot.pcolormesh(lone, late, PDuct, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap=cmap)
        cplot.msk_grd_pcolormesh(lone, late, PDuct, np.logical_not(PDuct.mask).astype(int), ddeg=0.1, levels=np.arange(0,1.1,0.1), ticks=np.arange(0.05,1.0,0.1), title=title, outfile=outfile+'_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap=cmap, addmask=True)
    return

def calc_class4_A_duct(date, expt, ddir=mir5, min_lat=-100, GIOPS=True):

    if ( GIOPS ):
        lonn, latn, orca_area = read_grid.read_coord()
    else:
        lonn, latn, orca_area = read_grid.read_coord_riops()

    # The comparison with model should be with the analysis (or forecast) over that date.  Timestamp day+1
    datestr=check_date.check_date(date, outtype=str)
    dateint=int(datestr)
    adate = date + datetime.timedelta(days=1)
    YY, MM, DD = date.year, date.month, date.day
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(YY,MM,DD)

    anal_date, anal_diff = find_nearest_analysis(adate)
    if ( anal_diff != 0 ):
        print('Not an analysis cycle date', date)

    if ( min_lat > -90 ):
        ILAT=read_EN4.find_in_latitudes(LAT, [min_lat, 90])
        LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], ILAT)
    IBTH=read_EN4.find_both_valid_TS(QT, QS)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IBTH)
    IDEP=read_EN4.remove_minimum_depth(DEP, QT, min_depth=100.0)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IDEP)

    CW = soundspeed.sound_speed(DEP, SW, TW)
    TorF_list = find_mins_obs(CW, DEP, mp=False)
    TorF_narr = np.array(TorF_list).astype(int)
    IJPTS=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=False)

    __, __, Pduct, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_T', ddir=ddir, ensembles=list(range(1,21)), GIOPS=GIOPS)
    if ( GIOPS ):
        Nmask = read_grid.read_mask()[0]
    else:
        Nmask = read_grid.read_riops_mask()[0]

    Pduct_list=[]
    for ijpt in IJPTS:
        Pduct_list.append(Pduct[ijpt])
        Mduct_list.append(Nmask[ijpt])

    imsked = read_EN4.find_indices(Mduct_list, 0)
    ivalid = read_EN4.find_indices(Mduct_list, 1)

    LON_narr = LON[ivalid]
    LAT_narr = LAT[ivalid]
    TorF_narr = np.array(TorF_list).astype(int)[ivalid]
    Pduct_narr=np.array(Pduct_list)[ivalid]
    Mduct_narr=np.array(Mduct_list)[ivalid]

    BRSC=np.sum( np.square(Pduct_narr - TorF_narr) )
    nobs=len(TorF_narr)
    print('Brier Scores BRSC', BRSC)
    
    SPRD = np.sum( Pduct_narr * ( 1-Pduct_narr) )
    print('Spread Values SPRD', SPRD)
    
    class4_file='CSPEED/CLASS4/class4_'+expt+'_'+datestr+'.nc'
    variables=['lon', 'lat', 'obs', expt]
    fields=[LON_narr, LAT_narr, TorF_narr, Pduct_narr]
    for ifield, field in enumerate(fields):
        print('SHAPE', variables[ifield], field.shape)
    write_nc_grid.write_nc_1d(fields, variables, class4_file)
    
    ddate_file='CSPEED/CLASS4/'+expt+'_PDUCT_date.dat'
    datadatefile.add_to_file(dateint, np.array([float(nobs), BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL, SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL]), file=ddate_file)

    return BRSC, SPRD

def calc_class4_duct(date, ddir=mir5):

    # The comparison with model should be with the analysis (or forecast) over that date.  Timestamp day+1
    datestr=check_date.check_date(date, outtype=str)
    dateint=int(datestr)
    adate = date + datetime.timedelta(days=1)
    YY, MM, DD = date.year, date.month, date.day
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(YY,MM,DD)

    anal_date, anal_diff = find_nearest_analysis(adate)
    if ( anal_diff != 0 ):
        print('Not an analysis cycle date', date)

    IBTH=read_EN4.find_both_valid_TS(QT, QS)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IBTH)
    IDEP=read_EN4.remove_minimum_depth(DEP, QT, min_depth=100.0)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IDEP)

    CW = soundspeed.sound_speed(DEP, SW, TW)
    TorF_list = find_mins_obs(CW, DEP, mp=False)
    TorF_narr = np.array(TorF_list).astype(int)
    IJPTS=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=False)

    __, __, Pduct, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_T', ddir=ddir, ensembles=list(range(1,21)))
    if ( anal_diff == 0 ):
        __, __, Panal, __ = find_ducts_for_date(adate, anal=True, expt='GIOPS_T', ddir=ddir, ensembles=list(range(1,21)))
    else:
        Panal = np.nan*np.ones(Pduct.shape)
    __, __, Pdmi1, __ = find_ducts_for_date( date, anal=False, expt='GIOPS_T', ddir=ddir, ensembles=list(range(1,21)))
    __, __, Pctrl, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_T', ddir=ddir, ensembles=[0])
    __, __, Pgdps, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_320_GD', ddir=mir6, ensembles='d')
    __, __, Plagg, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_320_GD', ddir=mir6, ensembles='l')
    __, __, Pclim, __ = find_ducts_for_date(adate, anal=False, expt='GIOPS_320_GD', ddir=mir6, ensembles='c')
    Nmask = read_grid.read_mask()[0]

    Pduct_list=[]
    Panal_list=[]
    Pdmi1_list=[]
    Pctrl_list=[]
    Pgdps_list=[]
    Plagg_list=[]
    Pclim_list=[]
    Mduct_list=[]
    for ijpt in IJPTS:
        Pduct_list.append(Pduct[ijpt])
        Panal_list.append(Panal[ijpt])
        Pdmi1_list.append(Pdmi1[ijpt])
        Pctrl_list.append(Pctrl[ijpt])
        Pgdps_list.append(Pgdps[ijpt])
        Plagg_list.append(Plagg[ijpt])
        Pclim_list.append(Pclim[ijpt])
        Mduct_list.append(Nmask[ijpt])

    imsked = read_EN4.find_indices(Mduct_list, 0)
    ivalid = read_EN4.find_indices(Mduct_list, 1)

    LON_narr = LON[ivalid]
    LAT_narr = LAT[ivalid]
    TorF_narr = np.array(TorF_list).astype(int)[ivalid]
    Pduct_narr=np.array(Pduct_list)[ivalid]
    Panal_narr=np.array(Panal_list)[ivalid]
    Pdmi1_narr=np.array(Pdmi1_list)[ivalid]
    Pctrl_narr=np.array(Pctrl_list)[ivalid]
    Pgdps_narr=np.array(Pgdps_list)[ivalid]
    Plagg_narr=np.array(Plagg_list)[ivalid]
    Pclim_narr=np.array(Pclim_list)[ivalid]
    Mduct_narr=np.array(Mduct_list)[ivalid]

    BRSC=np.sum( np.square(Pduct_narr - TorF_narr) )
    BRAN=np.sum( np.square(Panal_narr - TorF_narr) )
    BRM1=np.sum( np.square(Pdmi1_narr - TorF_narr) )
    BRS1=np.sum( np.square(Pctrl_narr - TorF_narr) )
    BRGD=np.sum( np.square(Pgdps_narr - TorF_narr) )
    BRLG=np.sum( np.square(Plagg_narr - TorF_narr) )
    BRCL=np.sum( np.square(Pclim_narr - TorF_narr) )
    nobs=len(TorF_narr)
    print('Brier Scores BRSC', BRSC)
    print('Brier Scores BRAN', BRAN)
    print('Brier Scores BRM1', BRM1)
    print('Brier Scores BRS1', BRS1)
    print('Brier Scores BRGD', BRGD)
    print('Brier Scores BRLG', BRLG)
    print('Brier Scores BRCL', BRCL)
    
    SPRD = np.sum( Pduct_narr * ( 1-Pduct_narr) )
    SPAN = np.sum( Panal_narr * ( 1-Panal_narr) )
    SPM1 = np.sum( Pdmi1_narr * ( 1-Pdmi1_narr) )
    SPS1 = np.sum( Pctrl_narr * ( 1-Pctrl_narr) )
    SPGD = np.sum( Pgdps_narr * ( 1-Pgdps_narr) )
    SPLG = np.sum( Plagg_narr * ( 1-Plagg_narr) )
    SPCL = np.sum( Pclim_narr * ( 1-Pclim_narr) )
    print('Spread Values SPRD', SPRD)
    print('Spread Values SPAN', SPAN)
    print('Spread Values SPM1', SPM1)
    print('Spread Values SPS1', SPS1)
    print('Spread Values SPGD', SPGD)
    print('Spread Values SPLG', SPLG)
    print('Spread Values SPCL', SPCL)
    
    class4_file='CSPEED/CLASS4/class4_pduct_'+datestr+'.nc'
    variables=['lon', 'lat', 'obs', 'GEPS', 'GPAN', 'GEP1', 'GEP0', 'GDPS', 'GLAG', 'GCLM']
    fields=[LON_narr, LAT_narr, TorF_narr, Pduct_narr, Panal_narr, Pdmi1_narr, Pctrl_narr, Pgdps_narr, Plagg_narr, Pclim_narr]
    for ifield, field in enumerate(fields):
        print('SHAPE', variables[ifield], field.shape)
    write_nc_grid.write_nc_1d(fields, variables, class4_file)
    
    ddate_file='CSPEED/CLASS4/PDUCT_date.dat'
    datadatefile.add_to_file(dateint, np.array([float(nobs), BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL, SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL]), file=ddate_file)

    return [BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL], [SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL]

syndir='/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs' 
outdir='/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBS1'
def calc_class4_duct_SYNOBS(date, dirlist=syndir, keylist=['CNTL', 'Free', 'NoArgo', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'Oper', 'SSTonly', 'NoAlt'], 
       explist=None, enslist='d', anllist=False, glolist=True, latsin=[-90, 90], odir=outdir):

    print('KEYLIST', keylist)
    if ( isinstance(explist, type(None)) ): expdict=dict(zip(keylist, keylist))
    if ( isinstance(explist, list) ): expdict=dict(zip(keylist, explist))
    if ( isinstance(explist, dict) ): expdict=explist
    
    if ( isinstance(dirlist, str) ): dirdict=dict(zip(keylist, [dirlist]*len(keylist)))
    if ( isinstance(dirlist, list) ): dirdict=dict(zip(keylist, dirlist))
    if ( isinstance(dirlist, dict) ): dirdict=dirlist

    if ( isinstance(enslist, type(None)) ): ensdict=dict(zip(keylist, ['d']*len(keylist)))
    if ( isinstance(enslist, str) ): ensdict=dict(zip(keylist, [enslist]*len(keylist)))
    if ( isinstance(enslist, list) ): ensdict=dict(zip(keylist, enslist))
    if ( isinstance(enslist, dict) ): ensdict=enslist

    if ( isinstance(anllist, type(None)) ): anldict=dict(zip(keylist, [False]*len(keylist)))
    if ( isinstance(anllist, bool) ): anldict=dict(zip(keylist, [anllist]*len(keylist)))
    if ( isinstance(anllist, list) ): anldict=dict(zip(keylist, anllist))
    if ( isinstance(anllist, dict) ): anldict=anllist
    
    if ( isinstance(glolist, type(None)) ): glodict=dict(zip(keylist, [True]*len(keylist)))
    if ( isinstance(glolist, bool) ): glodict=dict(zip(keylist, [glolist]*len(keylist)))
    if ( isinstance(glolist, list) ): glodict=dict(zip(keylist, glolist))
    if ( isinstance(glolist, dict) ): glodict=glolist

    if ( isinstance(latsin, float) or isinstance(latsin, int) ):
        latsin = [float(latsin), 90.0]
           
    # The comparison with model should be with the analysis (or forecast) over that date.  Timestamp day+1
    datestr=check_date.check_date(date, outtype=str)
    dateint=int(datestr)
    adate = date + datetime.timedelta(days=1)
    YY, MM, DD = date.year, date.month, date.day
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(YY,MM,DD)

    anal_date, anal_diff = find_nearest_analysis(adate)

    print("LATSIN", latsin)
    if ( ( not isinstance(latsin, type(None)) ) and ( not (latsin == [-90, 90] ) ) ):
        print("Subsetting OBS by latitude", latsin)
        ILAT=read_EN4.find_in_latitudes(LAT, latsin)
        LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], ILAT)
    IBTH=read_EN4.find_both_valid_TS(QT, QS)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IBTH)
    IDEP=read_EN4.remove_minimum_depth(DEP, QT, min_depth=100.0)
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IDEP)
    LON_narr = LON
    LAT_narr = LAT

    CW = soundspeed.sound_speed(DEP, SW, TW)
    TorF_LIST = find_mins_obs(CW, DEP, mp=False)
    TorF_narr = np.array(TorF_LIST).astype(int)

    Probs = dict(zip(keylist, [None]*len(keylist)))
    BRSCs = dict(zip(keylist, [None]*len(keylist)))
    SPRDs = dict(zip(keylist, [None]*len(keylist)))

    #IJPTS_list = []
    #Nmask_list = []
    #Mduct_list = []
    for akey in keylist:
        is_GIOPS = glodict[akey]
        if ( is_GIOPS ):
            lonn, latn, orca_area = read_grid.read_coord()
            Nmask = read_grid.read_mask()[0]
        else:
            lonn, latn, orca_area = read_grid.read_coord_riops()
            Nmask = read_grid.read_riops_mask()[0]
        IJPTS=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=False)
        
        Mduct_LIST=[]
        for ijpt in IJPTS:
            Mduct_LIST.append(Nmask[ijpt])
        imsked = read_EN4.find_indices(Mduct_LIST, 0)
        ivalid = read_EN4.find_indices(Mduct_LIST, 1)
        #LON_narr = LON[ivalid]
        #LAT_narr = LAT[ivalid]

        #TorF_narr = np.array(TorF_LIST).astype(int)[ivalid]
        #Mduct_narr=np.array(Mduct_LIST)[ivalid]

        print('INPUTS', akey, anldict[akey], expdict[akey], dirdict[akey], ensdict[akey])
        __, __, Pduct, __ = find_ducts_for_date(adate, anal=anldict[akey], expt=expdict[akey], ddir=dirdict[akey], ensembles=ensdict[akey], GIOPS=is_GIOPS, )
        #Probs[akey] = Pduct
        Pduct_list = []
        for ijpt in IJPTS:
            Pduct_list.append(Pduct[ijpt])
        Pduct_narr=np.array(Pduct_list)
        Pduct_narr=np.ma.array(Pduct_narr, mask=np.zeros(Pduct_narr.shape))
        Pduct_narr[imsked] = np.NaN
        Pduct_narr.mask[imsked] = True
        BRSC=np.nansum( np.square(Pduct_narr - TorF_narr) )
        SPRD = np.nansum( Pduct_narr * ( 1-Pduct_narr) )
        Probs[akey] = Pduct_narr
        BRSCs[akey] = BRSC
        SPRDs[akey] = SPRD

    nobs=len(TorF_narr)
    
    class4_file=odir+'/class4_pduct_'+datestr+'.nc'
    variables=['lon', 'lat', 'obs']+keylist
    fields=[LON_narr, LAT_narr, TorF_narr]+[Probs[akey] for akey in keylist]
    for ifield, field in enumerate(fields):
        print('SHAPE', variables[ifield], field.shape)
    write_nc_grid.write_nc_1d(fields, variables, class4_file)
    
    ddate_file=odir+'/PDUCT_date.dat'
    datadatefile.add_to_file(dateint, np.array([float(nobs)]+[BRSCs[akey] for akey in keylist]+[SPRDs[akey] for akey in keylist]), file=ddate_file)

    return Probs, BRSCs, SPRDs

def calc_class4_duct_cycle(date):
    date1=date - datetime.timedelta(days=7)
    date2=date - datetime.timedelta(days=1)
    dates=rank_histogram.create_dates(date1, date2, 1)
    for cdate in dates:
        [BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL], [SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL]  = calc_class4_duct(cdate)
    return

def calc_class4_duct_SYNOBS_cycle(date, dirlist=syndir, keylist=['CNTL', 'Free', 'NoArgo', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'Oper', 'SSTonly', 'NoAlt'], 
                                  explist=None, enslist='d', anllist=False, glolist=True, latsin=None, odir=outdir):
    print('KEYLIST', keylist)
    date1=date - datetime.timedelta(days=7)
    date2=date - datetime.timedelta(days=1)
    dates=rank_histogram.create_dates(date1, date2, 1)
    for cdate in dates:
        Probs, BRSCs, SPRDs  = calc_class4_duct_SYNOBS(cdate, dirlist=dirlist, keylist=keylist, explist=explist, enslist=enslist, anllist=anllist, glolist=glolist, latsin=latsin, odir=odir)
        print(BRSCs)
    return

def calc_class4_duct_stats(dates, ddir='CSPEED/CLASS4/', pdir='CSPEED/CLASS4/PLOTS/', filesuf='dates', ddeg=10.0, levels=np.arange(-0.45, 0.5, 0.1), ticks=np.arange(-0.4, 0.5, 0.1)):
    #all_lon, all_lat, all_obs, all_PEP, all_PAN, all_PE1, all_PC0, all_PGD, all_PLA, all_PCL = empty_all(10)
    if ( not dates ):
        files=glob.glob(add_slash(ddir)+'class4_pduct_????????.nc')
        dates=[]
        for file in files:
            dates.append(os.path.basename(file)[13:21])
        dates=sorted(dates)
        print(dates, len(dates))
    SUPER_LIST = empty_all(10)
    for date in dates:
        datestr=check_date.check_date(date, outtype=str)
        class4_file=add_slash(ddir)+'class4_pduct_'+datestr+'.nc'
        variables=['lon', 'lat', 'obs', 'GEPS', 'GPAN', 'GEP1', 'GEP0', 'GDPS', 'GLAG', 'GCLM']
        INPUT_list = write_nc_grid.read_nc_1d(class4_file, variables)
        #(lon, lat, TorF_narr, Pduct_narr, Panal_narr, Pdmi1_narr, Pctrl_narr, Pgdps_narr, Plagg_narr, Pclim_narr) = INPUT_list
        SUPER_LIST = extend_all(SUPER_LIST, INPUT_list)
        IBAD = np.where(np.square(INPUT_list[2]) > 1 )
        if ( len(IBAD[0]) > 0 ) : print(date, INPUT_list[2][IBAD])
        
    [all_lon, all_lat, all_obs, all_PEP, all_PAN, all_PE1, all_PC0, all_PGD, all_PLA, all_PCL] = SUPER_LIST   
    IBAD = np.where( np.square(all_obs) > 1 )
    IGOD = np.where( np.square(all_obs) < 1.01 ) 
    SUPER_LIST = read_EN4.replace_list_of_array(SUPER_LIST, IGOD)
    [all_lon, all_lat, all_obs, all_PEP, all_PAN, all_PE1, all_PC0, all_PGD, all_PLA, all_PCL] = SUPER_LIST   
    [all_lon, all_lat, all_obs] = SUPER_LIST[0:3]
    print('obs', np.min(all_obs), np.mean(all_obs), np.max(all_obs))
    SUPER_LIST = SUPER_LIST[3:]
    
    all_PAN = SUPER_LIST.pop(1)  ## pop out analysis which are reduced number of days
    all_PCL = SUPER_LIST[-1]
    
    IVLD = np.where(np.isfinite(all_PAN))
    pan_lon = all_lon[IVLD]
    pan_lat = all_lat[IVLD]
    pan_PAN = all_PAN[IVLD]
    pan_PCL = all_PCL[IVLD]
    pan_obs = all_obs[IVLD]
    
    BRIER_LIST = brier_all(SUPER_LIST, all_obs)
    SUPER_LAST = [pan_PAN, pan_PCL]
    BRIER_LAST = brier_all(SUPER_LAST, pan_obs)  ## NOTE:  SHOULD REDO WITH A SEPARATE PCL from analysis (PCL is from TRIAL).  REQUIRES RERUN DUCTS FOR DATE
    print('LEN', len(BRIER_LIST), len(BRIER_LAST), len(SUPER_LIST), len([pan_PAN, pan_PCL]))

    BRIER_LIST_LABELS=['Ensemble GIOPS', 'Day Plus One', 'Control Analysis', 'GIOPS', 'GIOPS Lagged', 'Model Climatology']
    BRIER_LAST_LABELS=['Analysis EnGIOPS', 'Model Climatology']

    grd_lon, grd_lat, BINNED_LIST, GLOBAL_LIST = bin_all(all_lon, all_lat, BRIER_LIST+[all_obs], ddeg=ddeg)
    __     , __     , BINNED_LAST, GLOBAL_LAST = bin_all(pan_lon, pan_lat, BRIER_LAST+[pan_obs], ddeg=ddeg)
    __     , __     , BPNNED_LIST, GPOBAL_LIST = bin_all(all_lon, all_lat, SUPER_LIST, ddeg=ddeg)
    __     , __     , BPNNED_LAST, GPOBAL_LAST = bin_all(pan_lon, pan_lat, SUPER_LAST, ddeg=ddeg)
   
    #global_PEP, global_PE1, global_PC0, global_PGD, global_PLA, global_PCL, global_OBS = GLOBAL_LIST
    global_OBS = GLOBAL_LIST.pop(-1)
    #binned_PEP, binned_PE1, binned_PC0, binned_PGD, binned_PLA, binned_PCL, binned_OBS = BINNED_LIST
    binned_OBS = BINNED_LIST.pop(-1)
    #global_PAN, global_PCA, global_OBA = GLOBAL_LAST
    global_OBA = GLOBAL_LAST.pop(-1)
    #binned_PAN, binned_PCA, binned_OBA = BINNED_LAST
    binned_OBA = BINNED_LAST.pop(-1)
    
    __     , __     , summed_OBS = cplot.binfld(all_lon, all_lat, np.ones(all_obs.shape), ddeg=ddeg, statistic='sum')
    __     , __     , summed_OBA = cplot.binfld(pan_lon, pan_lat, np.ones(pan_obs.shape), ddeg=ddeg, statistic='sum')

    global_BRS = global_OBS * (1.0 - global_OBS)   ##  I NEED TO PROVE THIS!!  BUT POSITIVE IT IS CORRECT!  GLOBAL BRIER SCORE.
    binned_CBS = binned_OBS * (1.0 - binned_OBS)   ##  SIMILIARLY THIS IS THE BINNED CLIMATOLOGICAL BRIER SCORE
    global_BRA = global_OBA * (1.0 - global_OBA)
    binned_CBA = binned_OBA * (1.0 - binned_OBA)

    glosum_OBS = np.sum(np.ones(all_obs.shape))
    glosum_OBA = np.sum(np.ones(pan_obs.shape))
    
    print('TOTAL OBS', glosum_OBS, len(all_obs), (glosum_OBS == len(all_obs)))
    print('ANALY OBS', glosum_OBA, len(pan_obs), (glosum_OBA == len(pan_obs)))
    
    #grp_lon, grp_lat, binned_PAN = cplot.binfld(pan_lon, pan_lat, pan_PCL-pan_PAN, ddeg=ddeg)
    #global_PAN = np.mean(pan_PCL-pan_PAN)
    #pansum_PCL = np.mean(pan_PCL)

    labels = BRIER_LIST_LABELS + BRIER_LAST_LABELS
    print('LEN', len(BINNED_LIST), len(BINNED_LAST))
    fields = [binned_CBS - binned_list for binned_list in BINNED_LIST] + [binned_CBA-binned_list for binned_list in BINNED_LAST]
    pields = BPNNED_LIST+BPNNED_LAST
    ofiles = ['PEP', 'PE1', 'PC0', 'PGD', 'PLA', 'PCL', 'PAN', 'PCA']
    ofiles = [ str(ifile)+'_'+ofile for ifile,ofile in enumerate(ofiles) ]
    nfiles = len(ofiles)
    ## NEED TO CHANGE
    GLOBAL_LIST = [global_BRS - globaf for globaf in GLOBAL_LIST]
    GLOBAL_LAST = [global_BRA - globaf for globaf in GLOBAL_LAST]
    global_list = [globaf/global_BRS for globaf in GLOBAL_LIST]
    global_last = [globaf/global_BRA for globaf in GLOBAL_LIST]
    print(BRIER_LIST_LABELS+BRIER_LAST_LABELS)
    print('Brier SKILL IMPROVEMENT', GLOBAL_LIST+GLOBAL_LAST)
    print('BRIER SKILL Score', global_list+global_last)

    outfiles = [add_slash(pdir) + filepre+'_BS_' + filesuf + ".png" for filepre in ofiles] 
    print('LEN', len(fields), len(global_list+global_last), len(labels), len(outfiles))
    plot_all(fields, global_list+global_last, grd_lon, grd_lat, labels, outfiles, title="Brier Score Improvement over Climatology", BSS=True, levels=levels, ticks=ticks, )
    outfiles = [add_slash(pdir) + filepre+'_PR_' + filesuf + ".png" for filepre in ofiles] 
    plot_all(pields, GPOBAL_LIST+GPOBAL_LAST, grd_lon, grd_lat, labels, outfiles, title="Mean Probability Occurence", levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)
    outfiles = [add_slash(pdir) + filepre+'_PD_' + filesuf + ".png" for filepre in ofiles] 
    plot_all([binned_prob-binned_OBS for binned_prob in BPNNED_LIST]+[binned_prob-binned_OBA for binned_prob in BPNNED_LAST], [prob-global_OBS for prob in GPOBAL_LIST]+[prob-global_OBA for prob in GPOBAL_LAST], grd_lon, grd_lat, labels, outfiles, title="Mean Probability (Frequency) BIAS", levels=levels, ticks=ticks, cmap=cmap_anom)
    
    outfile=add_slash(pdir) + str(nfiles)+'_OBS_BS_'+  filesuf + ".png"
    plot_all([binned_CBS], [global_BRA], grd_lon, grd_lat, ['Observed Climatology Brier Score'], [outfile], title='Mean Brier Score', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)
    outfile=add_slash(pdir) + str(nfiles)+'_OBS_PR_'+ filesuf + ".png"
    plot_all([binned_OBS], [global_OBS], grd_lon, grd_lat, ['Observed Probability'], [outfile], title='Mean Probability of Occurence', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)
    outfile=add_slash(pdir) + str(nfiles)+'_OBS_SM_'+ filesuf + ".png"
    plot_all([summed_OBS], [glosum_OBS], grd_lon, grd_lat, ['Total Observations'], [outfile], title='Observations in Bin', levels=np.arange(0, 1001, 100), ticks=None, cmap=cmap_full, glbavg=False)
    nfiles += 1

    outfile=add_slash(pdir) + str(nfiles)+'_OBA_BS_' + filesuf + ".png"
    plot_all([binned_CBA], [global_BRA], grd_lon, grd_lat, ['Clim Analysis Day Brier Score'], [outfile], title='Mean Brier Score', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)
    outfile=add_slash(pdir) + str(nfiles)+'_OBA_PR_' + filesuf + ".png"
    plot_all([binned_OBA], [global_OBA], grd_lon, grd_lat, ['Clim Analysis Day Brier Score'], [outfile], title='Mean Probability of Occurence', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)
    outfile=add_slash(pdir) + str(nfiles)+'_OBS_SM_' + filesuf + ".png"
    plot_all([summed_OBA], [glosum_OBA], grd_lon, grd_lat, ['Total Observations'], [outfile], title='Observations in Bin', levels=np.arange(0, 1001, 100), ticks=None, cmap=cmap_full, glbavg=False)
    nfiles += 1

    return 

def calc_class4_duct_stats_key(dates, reference='CNTL', keylist=['CNTL', 'Free', 'NoArgo', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'Oper', 'SSTonly', 'NoAlt'], 
                               ddir='CSPEED/SYNOBS/', pdir='CSPEED/SYNOBS/PLOTS/', filesuf='dates', ddeg=10.0,
                               levels=np.arange(-0.45, 0.5, 0.1), ticks=np.arange(-0.4, 0.5, 0.1), check_masked=False):
    
    iref=keylist.index(reference)
    nflds=len(keylist)
    #all_lon, all_lat, all_obs, all_PEP, all_PAN, all_PE1, all_PC0, all_PGD, all_PLA, all_PCL = empty_all(10)
    if ( not dates ):
        files=glob.glob(add_slash(ddir)+'class4_pduct_????????.nc')
        dates=[]
        for file in files:
            dates.append(os.path.basename(file)[13:21])
        dates=sorted(dates)
        print(dates, len(dates))
    SUPER_LIST = empty_all(3+nflds)
    for date in dates:
        datestr=check_date.check_date(date, outtype=str)
        class4_file=add_slash(ddir)+'class4_pduct_'+datestr+'.nc'
        variables=['lon', 'lat', 'obs']+keylist
        INPUT_list = write_nc_grid.read_nc_1d(class4_file, variables)
        #(lon, lat, TorF_narr, Pduct_narr, Panal_narr, Pdmi1_narr, Pctrl_narr, Pgdps_narr, Plagg_narr, Pclim_narr) = INPUT_list
        SUPER_LIST = extend_all(SUPER_LIST, INPUT_list)
        IBAD = np.where(np.square(INPUT_list[2]) > 1 )
        if ( len(IBAD[0]) > 0 ) : print(date, INPUT_list[2][IBAD])
        
    [all_lon, all_lat, all_obs] = SUPER_LIST[0:3]   
    IBAD = np.where( np.square(all_obs) > 1 )
    IGOD = np.where( np.square(all_obs) < 1.01 ) 
    SUPER_LIST = read_EN4.replace_list_of_array(SUPER_LIST, IGOD)
    if ( check_masked ):
        for ivar in range(len(keylist)):
            IBAD = np.where( SUPER_LIST[3+ivar].mask == True )
            IGOD = np.where( SUPER_LIST[3+ivar].mask == False )
            SUPER_LIST = read_EN4.replace_list_of_array(SUPER_LIST, IGOD)
            print( keylist[ivar], len(IBAD[0]))
            #if ( len(IBAD[0]) > 0 ) : print(keylist[ivar], INPUT_list[ivar][IBAD])
    [all_lon, all_lat, all_obs] = SUPER_LIST[0:3]
    print('obs', np.min(all_obs), np.mean(all_obs), np.max(all_obs), np.sum(all_obs))
    SUPER_LIST = SUPER_LIST[3:]
    BRIER_LIST = brier_all(SUPER_LIST, all_obs)
    BRS_REF = BRIER_LIST[iref]   # DO NOT pop reference
    PRB_REF = SUPER_LIST[iref]
    BRIER_LIST_LABELS=[akey for akey in keylist]

    IVLD = np.where(np.isfinite(BRS_REF))
    vld_lon = all_lon[IVLD]
    vld_lat = all_lat[IVLD]
    vld_obs = all_obs[IVLD]
    vld_BRS_REF = BRS_REF[IVLD]
    vld_PRB_REF = PRB_REF[IVLD]
    vld_BRIER_LIST = read_EN4.replace_list_of_array(BRIER_LIST, IVLD)
    vld_SUPER_LIST = read_EN4.replace_list_of_array(SUPER_LIST, IVLD)
    BRIER_SKILL = [ vld_BRS_REF - vld_BRS  for vld_BRS in vld_BRIER_LIST ]   # POSITIVE IS GOOD for score being compared with Reference score (smaller scores are better)
    global_REF = np.mean(vld_BRS_REF)

    ## NOTE:  THIS REDEFINDES BRIER_LIST ::  WHICH IS NO LONGER NEEDED
    grd_lon, grd_lat, BRIER_LIST, GLOBAL_BRIER_LIST = bin_all(vld_lon, vld_lat, vld_BRIER_LIST, ddeg=ddeg)
    __     , __     , PROBL_LIST, GLOBAL_PROBL_LIST = bin_all(vld_lon, vld_lat, vld_SUPER_LIST, ddeg=ddeg)
    #for binned in BRIER_LIST:
    #    print(binned.shape)
    
    #gro_lon, gro_lat, (binned_OBS, summed_OBS, binned_REF), (global_OBS, glosum_OBS, global_REF) = bin_all(vld_lon, vld_lat, [vld_obs, np.ones(vld_obs.shape), vld_BRS_REF])
    gro_lon, gro_lat, binned_probl_OBS = cplot.binfld(vld_lon, vld_lat, vld_obs, ddeg=ddeg)
    __     , __     , summed_count_OBS = cplot.binfld(vld_lon, vld_lat, np.ones(vld_obs.shape), ddeg=ddeg, statistic='sum')
    __     , __     , binned_brier_REF = cplot.binfld(vld_lon, vld_lat, vld_BRS_REF, ddeg=ddeg)
    __     , __     , binned_probl_REF = cplot.binfld(vld_lon, vld_lat, vld_PRB_REF, ddeg=ddeg)
    binned_brier_OBS = binned_probl_OBS * (1.0 - binned_probl_OBS)   ##  SIMILIARLY THIS IS THE BINNED CLIMATOLOGICAL BRIER SCORE
    
    ISOUTH = np.where(vld_lat < -30 )
    INORTH = np.where(vld_lat >  30 )

    global_probl_OBS = np.mean(vld_obs)
    global_brier_OBS = global_probl_OBS * (1.0 - global_probl_OBS)   ##  I NEED TO PROVE THIS!!  BUT POSITIVE IT IS CORRECT!  GLOBAL BRIER SCORE.
    global_count_OBS = np.sum(np.ones(vld_obs.shape))
    global_brier_REF = np.mean(vld_BRS_REF)
    global_probl_REF = np.mean(vld_PRB_REF)
    global_brier_skill_ref = [(global_brier_REF - global_brier) / global_brier_REF for global_brier in GLOBAL_BRIER_LIST]
    global_brier_skill_obs = [(global_brier_OBS - global_brier) / global_brier_OBS for global_brier in GLOBAL_BRIER_LIST]
    GLOBAL_PROBL_DIFF = [(global_probl - global_probl_OBS)  for global_probl in GLOBAL_PROBL_LIST]
    #print('TOTAL OBS', global_count_OBS, len(vld_obs), (global_count_OBS == len(all_obs)))

    NORTH_BRIER_LIST = subset_mean(INORTH, vld_BRIER_LIST, func=np.mean)
    NORTH_PROBL_LIST = subset_mean(INORTH, vld_SUPER_LIST, func=np.mean)
    north_probl_OBS = subset_mean(INORTH, vld_obs, func=np.mean)
    north_brier_OBS = north_probl_OBS * ( 1-north_probl_OBS )
    north_count_OBS = subset_mean(INORTH, np.ones(vld_obs.shape), func=np.sum)
    north_brier_REF = NORTH_BRIER_LIST[iref]
    north_probl_REF = NORTH_PROBL_LIST[iref]
    north_brier_skill_ref = [(north_brier_REF - north_brier) / north_brier_REF for north_brier in NORTH_BRIER_LIST]
    north_brier_skill_obs = [(north_brier_OBS - north_brier) / north_brier_OBS for north_brier in NORTH_BRIER_LIST]
    NORTH_PROBL_DIFF = [north_probl - north_probl_OBS for north_probl in NORTH_PROBL_LIST]
    
    SOUTH_BRIER_LIST = subset_mean(ISOUTH, vld_BRIER_LIST, func=np.mean)
    SOUTH_PROBL_LIST = subset_mean(ISOUTH, vld_SUPER_LIST, func=np.mean)
    south_probl_OBS = subset_mean(ISOUTH, vld_obs, func=np.mean) 
    south_brier_OBS = south_probl_OBS * ( 1-south_probl_OBS )
    south_count_OBS = subset_mean(ISOUTH, np.ones(vld_obs.shape), func=np.sum)
    south_brier_REF = SOUTH_BRIER_LIST[iref]
    south_probl_REF = SOUTH_PROBL_LIST[iref]
    south_brier_skill_ref = [(south_brier_REF - south_brier) / south_brier_REF for south_brier in SOUTH_BRIER_LIST]
    south_brier_skill_obs = [(south_brier_OBS - south_brier) / south_brier_OBS for south_brier in SOUTH_BRIER_LIST]
    SOUTH_PROBL_DIFF = [south_probl - south_probl_OBS for south_probl in SOUTH_PROBL_LIST]


    # Remove binned results where number of observations is less then 50
    obs_threshold = 50
    obs_threshold = 1
    BRIER_LIST = remove_from_bin(BRIER_LIST, summed_count_OBS, obs_threshold)
    PROBL_LIST = remove_from_bin(PROBL_LIST, summed_count_OBS, obs_threshold)
    binned_brier_REF = remove_from_bin(binned_brier_REF, summed_count_OBS, obs_threshold)
    binned_brier_OBS = remove_from_bin(binned_brier_OBS, summed_count_OBS, obs_threshold)
    binned_probl_OBS = remove_from_bin(binned_probl_OBS, summed_count_OBS, obs_threshold)
    BRIER_LIST_REF = [binned_brier_REF - binned_brier for binned_brier in BRIER_LIST] 
    BRIER_LIST_CLM = [binned_brier_OBS - binned_brier for binned_brier in BRIER_LIST] 
    PROBL_DIFF = [binned_prob - binned_probl_OBS for binned_prob in PROBL_LIST]

    labels = BRIER_LIST_LABELS
    ofiles = BRIER_LIST_LABELS
    global_brier_skill_ref = [(global_brier_REF - global_brier) / global_brier_REF for global_brier in GLOBAL_BRIER_LIST]
    global_brier_skill_obs = [(global_brier_OBS - global_brier) / global_brier_OBS for global_brier in GLOBAL_BRIER_LIST]

    print(BRIER_LIST_LABELS)
    print('obs clim ', global_brier_OBS, ' Brier Score ', GLOBAL_BRIER_LIST)
    print('BRIER SKILL Score wrt clim', global_brier_skill_obs)
    print('BRIER SKILL Score wrt '+reference, global_brier_skill_ref)
    print('obs clim ', global_probl_OBS, ' Frequency ', GLOBAL_PROBL_LIST)
    print('obs clim ', global_brier_OBS, ' Brier Score ', [global_brier_OBS - global_brier_skill*global_brier_OBS for global_brier_skill in global_brier_skill_obs])

    print("NORTH EXTRATROPICS")
    print(BRIER_LIST_LABELS)
    print('obs clim ', north_brier_OBS, ' Brier Score ', NORTH_BRIER_LIST)
    print('BRIER SKILL Score wrt clim', north_brier_skill_obs)
    print('BRIER SKILL Score wrt '+reference, north_brier_skill_ref)
    print('obs clim ', north_probl_OBS, ' Frequency ', NORTH_PROBL_LIST)
    print('obs clim ', north_brier_OBS, ' Brier Score ', [north_brier_OBS -north_brier_skill for north_brier_skill in north_brier_skill_obs])

    print("SOUTH EXTRATROPICS")
    print(BRIER_LIST_LABELS)
    print('obs clim ', south_brier_OBS, ' Brier Score ', SOUTH_BRIER_LIST)
    print('BRIER SKILL Score wrt clim', south_brier_skill_obs)
    print('BRIER SKILL Score wrt '+reference, south_brier_skill_ref)
    print('obs clim ', south_probl_OBS, ' Frequency ', SOUTH_PROBL_LIST)
    print('obs clim ', south_brier_OBS, ' Brier Score ', [south_brier_OBS - south_brier_skill for south_brier_skill in south_brier_skill_obs])
    ## GLOBAL
    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_bs_" + filesuf + ".png" for filepre in ofiles] 
    plot_all(BRIER_LIST, GLOBAL_BRIER_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0, 0.30, 0.02), ticks=np.arange(0,0.3,0.1), title = 'Brier Score', cmap=cmap_full)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsr_" + filesuf + ".png" for filepre in ofiles] 
    plot_all(BRIER_LIST_REF, global_brier_skill_ref, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over '+reference, cmap=cmap_anom)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsc_" + filesuf + ".png" for filepre in ofiles] 
    plot_all(BRIER_LIST_CLM, global_brier_skill_obs, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over obs clim', cmap=cmap_anom)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_prd_" + filesuf + ".png" for filepre in ofiles] 
    plot_all(PROBL_DIFF, GLOBAL_PROBL_DIFF, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Probabality (Frequency) Bias', cmap=cmap_anom)

    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_prb_" + filesuf + ".png" for filepre in ofiles] 
    plot_all(PROBL_LIST, GLOBAL_PROBL_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), title = 'Average Probability in Bin', cmap=cmap_full)
    
    # positive definite
    outfile=add_slash(pdir) + 'OBS'+ "_" + filesuf + ".png"
    plot_all([binned_probl_OBS], [global_probl_OBS], grd_lon, grd_lat, ['Climatological Probability'], [outfile], title = 'Probable Occurence in Bin', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full)

    # positive definite and LARGE
    outfile=add_slash(pdir) + 'SUM'+ "_" + filesuf + ".png"
    plot_all([summed_count_OBS], [global_count_OBS], grd_lon, grd_lat, ['Total Observations'], [outfile], title = 'Total Observations in Bin', levels=np.arange(0, 1001, 50), ticks=None, cmap=cmap_full)

    ## NORTH
    project='NorthPolarStereo'
    box=[-180, 180, 30, 90]
    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_bs_" + filesuf + ".np.png" for filepre in ofiles] 
    plot_all(BRIER_LIST, NORTH_BRIER_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0, 0.30, 0.02), ticks=np.arange(0,0.3,0.1), title = 'Brier Score', cmap=cmap_full, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsr_" + filesuf + ".np.png" for filepre in ofiles] 
    plot_all(BRIER_LIST_REF, north_brier_skill_ref, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over '+reference, cmap=cmap_anom, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsc_" + filesuf + ".np.png" for filepre in ofiles] 
    plot_all(BRIER_LIST_CLM, north_brier_skill_obs, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over obs clim', cmap=cmap_anom, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_prd_" + filesuf + ".np.png" for filepre in ofiles] 
    plot_all(PROBL_DIFF, NORTH_PROBL_DIFF, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Probabality (Frequency) Bias', cmap=cmap_anom, project=project, box=box)

    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_prb_" + filesuf + ".np.png" for filepre in ofiles] 
    plot_all(PROBL_LIST, NORTH_PROBL_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), title = 'Average Probability in Bin', cmap=cmap_full, project=project, box=box)
    
    # positive definite
    outfile=add_slash(pdir) + 'OBS'+ "_" + filesuf + ".np.png"
    plot_all([binned_probl_OBS], [north_probl_OBS], grd_lon, grd_lat, ['Climatological Probability'], [outfile], title = 'Probable Occurence in Bin', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full, project=project, box=box)

    # positive definite and LARGE
    outfile=add_slash(pdir) + 'SUM'+ "_" + filesuf + ".np.png"
    plot_all([summed_count_OBS], [north_count_OBS], grd_lon, grd_lat, ['Total Observations'], [outfile], title = 'Total Observations in Bin', levels=np.arange(0, 1001, 50), ticks=None, cmap=cmap_full, project=project, box=box)

    ## SOUTH
    project='SouthPolarStereo'
    box=[-180, 180, -90, -30]
    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_bs_" + filesuf + ".sp.png" for filepre in ofiles] 
    plot_all(BRIER_LIST, SOUTH_BRIER_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0, 0.30, 0.02), ticks=np.arange(0,0.3,0.1), title = 'Brier Score', cmap=cmap_full, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsr_" + filesuf + ".sp.png" for filepre in ofiles] 
    plot_all(BRIER_LIST_REF, south_brier_skill_ref, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over '+reference, cmap=cmap_anom, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_bsc_" + filesuf + ".sp.png" for filepre in ofiles] 
    plot_all(BRIER_LIST_CLM, south_brier_skill_obs, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Brier Score improvement over obs clim', cmap=cmap_anom, project=project, box=box)

    # 0 centered
    outfiles = [add_slash(pdir) + filepre + "_prd_" + filesuf + ".sp.png" for filepre in ofiles] 
    plot_all(PROBL_DIFF, SOUTH_PROBL_DIFF, grd_lon, grd_lat, labels, outfiles, levels=levels, ticks=ticks, title = 'Probabality (Frequency) Bias', cmap=cmap_anom, project=project, box=box)

    # positive definite
    outfiles = [add_slash(pdir) + filepre + "_prb_" + filesuf + ".sp.png" for filepre in ofiles] 
    plot_all(PROBL_LIST, SOUTH_PROBL_LIST, grd_lon, grd_lat, labels, outfiles, levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), title = 'Average Probability in Bin', cmap=cmap_full, project=project, box=box)
    
    # positive definite
    outfile=add_slash(pdir) + 'OBS'+ "_" + filesuf + ".sp.png"
    plot_all([binned_probl_OBS], [south_probl_OBS], grd_lon, grd_lat, ['Climatological Probability'], [outfile], title = 'Probable Occurence in Bin', levels=np.arange(0,1.01,0.05), ticks=np.arange(0,1.1,0.1), cmap=cmap_full, project=project, box=box)

    # positive definite and LARGE
    outfile=add_slash(pdir) + 'SUM'+ "_" + filesuf + ".sp.png"
    plot_all([summed_count_OBS], [south_count_OBS], grd_lon, grd_lat, ['Total Observations'], [outfile], title = 'Total Observations in Bin', levels=np.arange(0, 1001, 50), ticks=None, cmap=cmap_full, project=project, box=box)

    return 

def subset_mean(IPTS, GRID, func=np.mean ):
    if ( isinstance(GRID, list) ):
        MN = []
        for grid in GRID:
            MN.append(subset_mean(IPTS, grid, func=func))
        return MN
    if ( isinstance(IPTS, type(None) ) ):
        SUBGRID = GRID[:]
    else:
        SUBGRID = GRID[IPTS]
    MN = func(SUBGRID)
    return MN
    
def empty_all(N):
    return_list = []
    for ii in range(N):
        return_list.append([])
    return return_list
    
def extend_all(input_list, extend_list):
    nlist = len(input_list)
    output_list = []
    for ilist in range(nlist):
        output_list.append(np.ma.append(input_list[ilist], extend_list[ilist], axis=0))
    return output_list

def brier_all(input_list, obs):
    nlist = len(input_list)
    brier_list = []
    for ilist in range(nlist):
        brier_list.append(np.square(input_list[ilist] - obs))
    return brier_list

def plot_all(fields, glvals, lon, lat, labels, ofiles, 
             levels=np.arange(-0.225, 0.226, 0.05), ticks=np.arange(-0.2, 0.21, 0.05), 
             title = 'Brier Score improvement over climatology', cmap=cmap_anom, glbavg=True, BSS=False,
             project='PlateCarree', box=[-180, 180, -90, 90] ):
    obar = 'horizontal'
    make_global=False
    if ( box == [-180, 180, -90, 90] ): make_global=True
    if ( project == 'NorthPolarStereo' ): obar='vertical'
    if ( project == 'SouthPolarStereo' ): obar='vertical'
    nflds = len(fields)
    for ifld in range(nflds):
        field=fields[ifld]
        label=labels[ifld]
        ofile=ofiles[ifld]
        globv=glvals[ifld]
        bratext='glb.'
        if ( BSS ): bratext='BSS glb.'
        if ( glbavg ):
            xitle=title+' ('+bratext+'avg. = '+str(globv)+')'
        else:
            xitle=title+' ('+bratext+'sum. = '+str(globv)+')'
        cplot.pcolormesh( lon, lat, field, levels=levels, ticks=ticks, cmap=cmap, project=project, outfile=ofile, make_global=make_global, title=xitle, suptitle=label,  obar=obar, box=box)
    return

def bin_all(lon, lat, input_list, ddeg=2.0):
    nlist = len(input_list)
    binned_list = []
    global_list = []
    for ilist in range(nlist):
        field = input_list[ilist]
        grid_lon, grid_lat, binned_fld = cplot.binfld(lon, lat, field, ddeg=ddeg)
        binned_list.append(binned_fld)
        global_list.append(np.mean(field))
        print('Max/Min', np.min(field), np.mean(field), np.max(field))
    return grid_lon, grid_lat, binned_list, global_list

def remove_from_bin(field, qc_field, qc_threshold):   # What is the best python why to pass a criteria?  [I.e. <, >, ==]
    if ( isinstance(field, list) ):
        new_list = []
        for ifield in field:
            nfield = remove_from_bin(ifield, qc_field, qc_threshold)
            new_list.append(nfield)
        return new_list
    IRM = np.where(qc_field < qc_threshold)
    new_field = field.copy()
    new_field[IRM] = np.NaN
    return new_field
    
def add_slash(textstring):
   if ( textstring.endswith('/') ):
     newstring=textstring
   else: 
     newstring=textstring+'/'
   return newstring
