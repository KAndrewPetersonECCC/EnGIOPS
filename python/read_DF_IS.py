#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import datetime
import time
import numpy as np
import pickle
import pandas as pd

import multiprocessing
import itertools
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.dates as mdates
import subprocess

import ola_functions
import read_DF_VP
from read_DF_VP import get_mdir
import check_date
import inside_polygon
import nearest
import cplot

num_cpus = len(os.sched_getaffinity(0))
intconvfac=10000.0
test_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'
if not os.path.isfile(test_file):
    print("WARNING: TEST FILE NOT PRESENT")

cmap_anom = 'seismic'
cmap_zero = 'RdYlBu_r'
cmap_posd = 'gist_stern_r'


def SSH_dataframe(input_file, SAT='ALL'):
    df_IS = ola_functions.SSH_SAT_dataframe(input_file, SAT=SAT)
    return df_IS

def average_duplicate(df_SSH):
    """
    Average duplicate profiles in dataframe.'
    Required so ensemble members only have set of distinct profiles.
    """
    df_SSH_group = df_SSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['Lon', 'Lat', 'tt', 'obs', 'mod', 'ana', 'misfit', 'setID', 'oerr', 'TrackNum', 'QC']]
    df_SSH_nodupl = df_SSH_group.mean()
    df_SSH_nodupl.reset_index(drop=True, inplace=True)
    #CHECK
    df_SSH_group = df_SSH_nodupl.groupby(['Lat', 'Lon', 'tt'], as_index='False')
    COUNT = df_SSH_group.count()
    DUPL = COUNT[COUNT['misfit'] > 1]
    if ( ( len(DUPL) != 0 ) ):
        print('STILL DUPLICATES', DUPL)
    return df_SSH_nodupl

def read_member_SSH(expt, date, iens,  ddir=get_mdir(5),  check_duplicate=True, SAT='ALL'):  
    datestr8  = check_date.check_date(date, dtlen=8)
    datestr10 = check_date.check_date(date, dtlen=10)
    estr=str(iens)
    input_file=ddir+'/'+expt+estr+'/SAM2/'+datestr8+'/DIA/'+datestr10+'_SAM.ola'
    df_SSH = SSH_dataframe(input_file, SAT=SAT)
    if ( check_duplicate ):
        df_NU = average_duplicate(df_SSH)
    else:
        df_NU = df_SSH.copy()
    df_SSH['member'] = iens
    return df_NU 

def read_ensemble_SSH(expt, date, ddir=get_mdir(5), ens=list(range(21)), check_duplicate=True, mp_read=True, SAT='ALL'):
    nens = len(ens)
    df_list = []
    if ( not mp_read ):  
        df_list = []
        for ie in ens:
            df_IE = read_member_SSH(expt, date, ie, ddir=ddir, check_duplicate=check_duplicate, SAT=SAT)
            df_list.append(df_IE)
    else:
        nproc=min([num_cpus, nens])
        read_pool = multiprocessing.Pool(nproc)
        #read_pool = multiprocessing.pool.ThreadPool()
        izip= list(zip(itertools.repeat(expt), itertools.repeat(date), ens))
        df_list = read_pool.starmap(partial(read_member_SSH, ddir=ddir, check_duplicate=check_duplicate, SAT=SAT), izip)
        #result_list = read_pool.starmap_async(partial(read_member_VP, ddir=ddir, check_duplicate=check_duplicate), izip)
        read_pool.close()
        read_pool.join()
        #for df_ie in result_list.get():
        #   df_list.append(df_ie)
    df_EnSSH = pd.concat(df_list).reset_index()
    return df_EnSSH    

def read_deterministic_SSH(expt, date, ddir=get_mdir(5), check_duplicate=True, SAT='ALL'):      
    datestr8  = check_date.check_date(date, dtlen=8)
    datestr10 = check_date.check_date(date, dtlen=10)
    input_file= ddir+'/'+expt+'/SAM2/'+datestr8+'/DIA/'+datestr10+'_SAM.ola'
    df_list = [ SSH_dataframe(input_file, SAT=SAT) ]
    df_EnSSH = pd.concat(df_list)
    return df_EnSSH    
 

def ensemble_average_SSH(df_EnSSH, count=21):
    # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['obs', 'mod', 'ana', 'misfit', 'setID', 'oerr', 'TrackNum', 'QC']]
    df_CNT = df_SSH.count()
    LT = len(df_CNT[df_CNT['misfit'] < count ])     
    print('Number of SubEnsembles = ', LT)    
    NT = len(df_CNT[df_CNT['misfit'] > count ])
    if ( NT > 0 ):
        print("WARNING:  Too many Ensemble Members")
        print(NT)
    df_EaSSH = df_SSH.mean().reset_index()
    df_varSSH = df_SSH.var(ddof=0).reset_index()
    df_EaSSH[['ensvar','varobs','varmod', 'varana']] = df_varSSH[['misfit', 'obs', 'mod', 'ana']].values   
    return df_EaSSH

def add_squared_error(df_SSH):
    df_NU = df_SSH.copy() 
    misfit = df_SSH['misfit'].values
    sqrerr = np.square(misfit)
    df_NU['sqrerr'] = sqrerr
    return df_NU


def add_crps_SSH(df_EaSSH, df_EnSSH):
    df_crps = calc_crps_SSH(df_EnSSH)
    df_NU = pd.concat([df_EaSSH, df_crps['crps']],axis=1)
    return df_NU
        

def calc_crps_SSH(df_EnSSH):
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['misfit']]
    df_crps = df_SSH.apply(lambda x: read_DF_VP.calc_crps(x.values.flatten(),0)).rename('crps').reset_index()
    return df_crps

    
def calc_crps_SSHf(df_EnSSH):
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['obs', 'mod']]
    df_crps = df_SSH.apply(lambda x: read_DF_VP.calc_crps(x['mod'].values.flatten(), x['obs'].mean())).rename('crps').reset_index()
    return df_crps


def calc_errors_date(date, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5), mp_read=True, SAT='ALL'):
    #mp_read = not mp   #  Need to find out how to run a child mp process inside another mp process.
    if ( deterministic ):
        df_EnSSH = read_deterministic_SSH(expt, date, ddir=ddir, SAT=SAT)
    else:
        df_EnSSH = read_ensemble_SSH(expt, date, ddir=ddir, ens=ens, mp_read=mp_read, SAT=SAT)
    df_EaSSH = ensemble_average_SSH(df_EnSSH)
    df_EaSSH = add_squared_error(df_EaSSH)
    df_EaSSH = add_crps_SSH(df_EaSSH, df_EnSSH)
    gl_series=summed_field(df_EaSSH)
    rgs_series = calc_region_errors(df_EaSSH)
    bin_series = sum_ongrid(df_EaSSH)
    return gl_series, rgs_series, bin_series
    

def average_field(df_EaSSH):
    df_Glave = df_EaSSH.mean()
    return df_Glave
def summed_field(df_EaSSH):
    df_Glsum = df_EaSSH.sum()
    count = df_EaSSH['misfit'].count()
    df_Glsum['count'] = count
    return df_Glsum

    
def calc_region_errors(df_EaSSH):
    regions = read_DF_VP.PAREAS.keys()
    rgs_series = []
    for region in regions:
        polygon = read_DF_VP.PAREAS[region]
        points_are_inside = inside_polygon.test_inside_xyarray(polygon, df_EaSSH['Lon'].values, df_EaSSH['Lat'].values)[0]
        df_region = df_EaSSH[points_are_inside]
        rg_series = summed_field(df_region)
        rgs_series.append(rg_series)
    return rgs_series


DELTA=1.0
def put_ongrid(df, delta=DELTA, latlon=['Lat', 'Lon']):
    df_g = df.copy()
    nomlat, nomlon = latlon
    bins_lons, bins_lats, xlon, xlat, query_lon, query_lat = read_DF_VP.nearest.grid(delta=delta)
    df_g['lat_bin'] = nearest.nearest3(query_lat, bins_lats, df[nomlat].values)
    df_g['lon_bin'] = nearest.nearest3(query_lon, bins_lons, df[nomlon].values)
    df_g.drop(latlon,axis=1)
    return df_g


ll_bin = ['lon_bin', 'lat_bin']     
def sum_ongrid(df_EaSSH, delta=DELTA):
    df_g = put_ongrid(df_EaSSH, delta=delta)   
    df_sum = df_g.groupby(['lon_bin', 'lat_bin']).sum().reset_index()
    df_cnt = df_g.groupby(['lon_bin', 'lat_bin']).count().reset_index()
    df_sup = pd.concat([df_sum, df_cnt['misfit'].rename('count')],axis=1)
    return df_sup


def init_dataframes():
    gl_series = read_DF_VP.init_df()
    bin_series = read_DF_VP.init_df()
    rgs_series = []
    for region in  read_DF_VP.PAREAS.keys():
        rg_sup = read_DF_VP.init_df()
        rgs_series.append(rg_sup)
    return gl_series, rgs_series, bin_series



def cycle_thru_dates(dates, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5),  mp_date=True,  mp_read=False, SAT='ALL', NP=20):
    print('ENTERING CYCLE THRU DATES', 'mp_date='+str(mp_date), 'mp_read='+str(mp_read), flush=True)
    gl_series, rgs_series, bin_series = init_dataframes()
    SSHvars = ['obs', 'mod', 'ana', 'oerr', 'misfit', 'sqrerr', 'crps', 'ensvar', 'varobs', 'varmod', 'varana', 'count']
    SSHaxis = ['Lat', 'Lon', 'tt']
    nvar = len(SSHvars)
    ntim = len(dates)
    nars = len(read_DF_VP.PAREAS.keys()) + 1
        
    tglrs = np.NaN * np.ones((ntim, nvar))
    tglrs_series = []
    for iarea in range(nars):
        tglrs_series.append([])
    
    ADD_RESULTS=[]
    time00=time.time()
    if (mp_date):
        #CAN't HANDLE FULL NUMBER OF PROCESSORS (MEMORY?)
        nproc=min([num_cpus, len(dates)])
        nproc=min([NP, num_cpus])
        print( 'NPROC', nproc, num_cpus, len(dates), flush=True )
        process_pool = multiprocessing.Pool(nproc)
        izip = list(zip(dates, itertools.repeat(expt)))
        #print(izip)
        RTN_LIST = process_pool.starmap_async(partial(calc_errors_date, ens=ens, deterministic=deterministic, ddir=ddir, mp_read=False, SAT=SAT), izip)
        process_pool.close()
        process_pool.join()
        ADD_RESULTS = RTN_LIST.get()
    else:     
       for idate,date in enumerate(dates):
           time0 = time.time()
           print("ENTERING DATE", date, flush=True)
           ADD_RESULTS.append(calc_errors_date(date, expt, ens=ens, deterministic=deterministic, ddir=ddir, mp_read=mp_read, SAT=SAT))
           print("SINGLE DATE TIME", time.time() - time0, flush=True)
    print("ALL DATE TIME", time.time() - time00, flush=True)
    for idate, date in enumerate(dates):
       add_gl_series, add_rgs_series, add_bin_series = ADD_RESULTS[idate]
       gl_series, rgs_series, bin_series = addto_sums( ( gl_series, rgs_series, bin_series ), (add_gl_series, add_rgs_series, add_bin_series) )
       day_gl_series, day_rgs_series = apply_averaging(add_gl_series, add_rgs_series)
       tglrs_series = addto_tlist(idate, tglrs_series, [day_gl_series]+day_rgs_series, SSHvars)

    # Apply Final Averaging on area averages
    gl_series_avg, rgs_series_avg = apply_averaging(gl_series, rgs_series, count_name='count', coord_list=SSHaxis)
    
    # Subset bin_series to Levels
    bin_series_avg = apply_bin_averaging(bin_series, count_name='count', llvars=['lon_bin', 'lat_bin'], extra=['tt'])
    print("FINAL DATE TIME", time.time() - time00, flush=True)
    return gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series



def addto_sums( old_sums, add_sums):
    gl_series, rgs_series, bin_series = old_sums
    add_gl_series, add_rgs_series, add_bin_series = add_sums
        
    gl_new = pd.concat([gl_series, add_gl_series], axis=1).sum(axis=1)
    #print(gl_new['count'])
                
    new_rgs_series = []
    for ir, rg_series in enumerate(rgs_series):
        add_rg_series = add_rgs_series[ir]
        rg_new = pd.concat([rg_series, add_rg_series], axis=1).sum(axis=1)
        #print(rg_new['count'])
        new_rgs_series.append(rg_new)
        
    gr_cat = pd.concat([bin_series, add_bin_series])
    gr_new = gr_cat.groupby(['lat_bin', 'lon_bin']).sum().reset_index()
        
    return gl_new, new_rgs_series, gr_new   


def final_mean( df_sum, count_name, coord_list ):
   df_avg = df_sum.copy()
   keys = df_avg.keys()
   keys = keys.drop(coord_list)
   
   for key in keys:
       if ( key != count_name ):
           df_avg[key] = df_sum[key] / df_sum[count_name]

   return df_avg   
   
   
   
def apply_averaging(gl_series, rgs_series, count_name='count', coord_list=['Lon', 'Lat', 'tt']):

    ald_series = rgs_series+[gl_series]
    ald_series_avg = []
    for sng_series in ald_series:
        avg = final_mean(sng_series, count_name, coord_list=coord_list)
        ald_series_avg.append(avg)
    rgs_series_avg = ald_series_avg[0:len(rgs_series)]
    gl_series_avg = ald_series_avg[-1]

    return gl_series_avg, rgs_series_avg


    
def apply_bin_averaging(Bin, count_name='count', llvars=['lon_bin', 'lat_bin'], extra=['tt']):
    newBin = Bin.copy()
    sumBin = newBin.groupby(llvars).sum().reset_index()
    avgBin = final_mean(sumBin, count_name, coord_list=llvars+extra )        
    return avgBin



def addto_array(idate, tglrs_series, rgs_series, SSHvars):
    nseries = len(rgs_series)
    for iseries, a_series in enumerate(rgs_series):
        tglrs = tglrs_series[iseries].copy()
        for ikey, key in enumerate(SSHvars):
            tglrs[idate, ikey] = a_series[key]
        tglrs_series[iseries] = tglrs.copy()
    return tglrs_series        

def addto_tlist(idate, tglrs_series, rgs_series, SSHvars):
    nseries = len(rgs_series)
    for iseries, a_series in enumerate(rgs_series):
        tglrs = tglrs_series[iseries].copy()
        tglrs.append(a_series[SSHvars])
        tglrs_series[iseries] = tglrs.copy()
    return tglrs_series        
        
def process_expt(dates, expt, ens_passed, this_ddir, mp_read=False, mp_date=True, SAT='ALL', NP=20):
    deterministic = False
    print(ens_passed)
    if ( ( isinstance(ens_passed, list) ) or ( isinstance(ens_passed, np.ndarray) ) ): ens = ens_passed
    if ( isinstance(ens_passed, type(None) ) ): deterministic = True
    if ( isinstance(ens_passed, int) ):
         if ( ens_passed == 0 ): 
             deterministic = True
             ens=0
         else:
             ens=list(range(ens_passed))
     
    if ( mp_date ): 
       mp_read_pass = False
    else:
       mp_read_pass = mp_read            
    gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series = cycle_thru_dates(dates, expt, ens=ens, deterministic=deterministic, ddir=this_ddir, mp_read=mp_read_pass, mp_date=mp_date, SAT=SAT, NP=NP)
    return  expt, gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series
     

def cycle_thru_expts(dates, expts, enss, ddir=get_mdir(5), mp_expt=False, mp_read=False, mp_date=True, SAT='ALL', NP=20):

    print( "MP SETTINGS", mp_expt, mp_date, mp_read, flush=True)

    gl_list = []
    rgs_list = []
    bin_list = []
    tglrs_list = []
    expt_list = []
    if ( isinstance(ddir, list) ): 
        ddirs=ddir
    else:
        ddirs = [ ddir for expt in expts ]

    time00 = time.time()
    if ( not mp_expt ):
        for iexpt, expt in enumerate(expts):
            time0 = time.time()
            ens_passed = enss[iexpt]
            dir_passed = ddirs[iexpt]
            expt_rtn, gl_series, rgs_series, bin_series, tglrs = process_expt(dates, expt, ens_passed, dir_passed, mp_read=mp_read, mp_date=mp_date, SAT=SAT, NP=NP)
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            tglrs_list.append(tglrs)
            expt_list.append(expt_rtn)
            time1 = time.time()
            print( 'Processing time ', iexpt, expt, time1-time0)
            print( 'Total Processing time ', iexpt, expt, time1-time00, flush=True)
    else:
        nproc=min([num_cpus, len(expts)])
        process_pool = multiprocessing.Pool(nproc)
        izip = list(zip(itertools.repeat(dates), expts, enss, ddirs))
        print(izip)
        RTN_LIST = process_pool.starmap_async(partial(process_expt, mp_read=False, mp_date=True, SAT=SAT), izip)
        process_pool.close()
        process_pool.join()
        FIN_LIST = RTN_LIST.get()
        sort_list = []
        for isort, fin_element in enumerate(FIN_LIST):
            expt_rtn, gl_series, rgs_series, bin_series, tglrs = fin_element
            if ( expt_rtn != expts[isort] ):
                print("WARNING: Experiments order not conserved!!")
                print(isort, expt_rtn, expts[isort])
            sort_list.append(expts.index(expt_rtn))
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            tglrs_list.append(tglrs)
            expt_list.append(expt_rtn)
        expt_copy = expt_list.copy()
        expt_list = [ expt_list[isort] for isort in sort_list ]
        gl_list = [ gl_list[isort] for isort in sort_list ]
        rgs_list = [ rgs_list[isort] for isort in sort_list ]
        bin_list = [ bin_list[isort] for isort in sort_list ]
        grgs_list = [ grgs_list[isort] for isort in sort_list ]
        print("SORTED ", ( list(expt_list) == list(expts) ), expt_list, expts, sort_list, expt_copy )
    time1 = time.time()
    print( 'Total cycle_thur_expts Processing time ', 'ALL EXPTS', time1-time00, flush=True)
    return gl_list, rgs_list, bin_list, tglrs_list

def produce_stats_plot( date_range, expts, enss, labels=None, outdir=None, ddir=get_mdir(5), mp_expt=False, mp_date=False, mp_read=False, outdirpre='', noensstat=False, SAT='ALL', NP=20, LEV_posd=None, LEV_anom=None, LEV_diff=None):
    SSHvars = ['obs', 'mod', 'ana', 'oerr', 'misfit', 'sqrerr', 'crps', 'ensvar', 'varobs', 'varmod', 'varana', 'count']
    dropvar = ['obs', 'ana', 'oerr', 'varobs', 'varmod', 'varana']
    SSHpass = [ var for var in SSHvars if var not in dropvar ]
    SSHvarslist =  ['count', 'misfit', 'sqrerr', 'ensvar', 'crps', 'mod']+['lon_bin', 'lat_bin']
    print(SSHpass, SSHvarslist)
    nexpts = len(expts)
    if ( mp_expt and mp_read ):
        print('WARNING:  1 Multitasking within multitasking not working')
        mp_read = False
    if ( mp_date and mp_read ):
        print('WARNING:  2 Multitasking within multitasking not working')
        mp_read = False
    if ( mp_date and mp_expt ):
        print('WARNING:  3 Multitasking within multitasking not working')
        mp_expt = False
    if ( len(date_range) > 3 ):
        dates=date_range
    elif ( len(date_range) == 1 ): 
        dates=date_range
    else:
        date_inc = 7
        if ( len(date_range) == 3 ): date_inc=date_range[2]
        date_inc = 7
        dates=rank_histogram.create_dates(date_range[0], date_range[1], date_inc)

    if ( labels is None ): labels=expts
    if ( outdir is None ): outdir=expts
    for odir in outdir:
        subprocess.call(['mkdir', outdirpre+odir])
    for odir in outdir[1:]:
        pdir=outdir[0]+'_'+odir
        subprocess.call(['mkdir', outdirpre+pdir])
    
    datestr0 = check_date.check_date(dates[0],  dtlen=8)
    datestr1 = check_date.check_date(dates[-1], dtlen=8)
    datestrr = datestr0 + '_' + datestr1
    gl_list, rgs_list, bin_list, tglrs_list = cycle_thru_expts(dates, expts, enss, ddir=ddir, mp_expt=mp_expt, mp_read=mp_read, mp_date=mp_date, SAT=SAT, NP=NP)
    print("FINISHED CYCLE THROUGH ALL EXPERIMENT DATES")

    nexpt=len(expts)
    for iexpt, expt in enumerate(expts):
        binL = bin_list[iexpt][SSHvarslist]
        outpreoutb=outdirpre+outdir[iexpt]+'/'+'SLA_'+datestrr+'_'
        titpre=labels[iexpt]+' '+datestrr
        print('TITLE', titpre, len(titpre))
        plot_df_field(binL, titpre=titpre, outpre=outpreoutb, drop=dropvar, LEV_posd=LEV_posd, LEV_anom=LEV_anom)
        print("FINISHED FULL FIELD SLA : ", labels[iexpt])
        if ( iexpt == 0 ): 
            bin0=binL
        else:
            odir=outdirpre+outdir[0]+'_'+outdir[iexpt]
            titpre=labels[0]+'-'+labels[iexpt]+' '+datestrr
            print('TITLE', titpre, len(titpre))
            outpreoutb=odir+'/'+'SLA_'+datestrr+'_'
            plot_diff_field(bin0, binL, titpre=titpre, outpre=outpreoutb, drop=dropvar, LEVS=LEV_diff)
            print("FINISHED DIFF FIELD SLA : ", labels[iexpt])
    print("FINISHED SLA PLOTS")

    narea = len(tglrs_list[0])
    narea = len(read_DF_VP.PAREAS.keys())+1
    for iarea in range(narea):
        tx_list = []
        for iexpt in range(nexpt):
            tglrs = tglrs_list[iexpt][iarea]
            tt_list = []
            for it, a_tglrs in enumerate(tglrs):
                aa_tglrs = a_tglrs[SSHvarslist]
                tt_list.append(aa_tglrs)
            tx_list.append(tt_list)
            
        print(tx_list[0][0].keys())
        plot_time_vars(dates, tx_list, labels, outdir[0], areanam, outdirpre=outdirpre)
    print("FINISHED TIMESERIES PLOTS")
            
    return

def plot_df_field(binF, drop=[], outpre='PLOTS/', titpre='', LEV_posd=None, LEV_anom=None):
   if ( isinstance(binF, list) or isinstance(binF, tuple) ): 
       for ibinF in binF:
           plot_df_field(ibinF, drop=drop, outpre=outpre)
       return
   binP = binF.copy()
   lon_bin = binF['lon_bin'].values
   lat_bin = binF['lat_bin'].values
   binP.drop(['lon_bin', 'lat_bin'], inplace=True, axis=1)
   for idrop in drop:
       if ( idrop in binP.keys() ): binP.drop([idrop], axis=1, inplace=True)

   print('Full Field', outpre, list(binP.keys()))   
   for vari in binP.keys():
       fld = binF[vari].values
       varn = vari
       LEVS = None
       if ( vari[0:6] == 'sqrerr' ):
           fld=np.sqrt(fld)
           varn='rmse'
           cmap = cmap_posd
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
       if ( vari[0:6] == 'ensvar' ):
           fld = np.sqrt(fld)
           varn='estd'
           cmap = cmap_posd
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
       if ( vari[0:6] == 'misfit' ):
           varn='merr'
           cmap=cmap_anom
           if ( isinstance(LEV_anom, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=False)
           else:
               LEVS=LEV_anom
       if ( vari[0:3] == 'mod' ):
           varn=vari
           LEVS = read_DF_VP.find_good_contour_levels(fld, posd=False)
           cmap = cmap_anom
       outfile=outpre+varn+'.png'
       print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn
       print(varn, 'Max/Min', np.max(fld), np.min(fld)) 
       # Attempting to plot zero fields (like ensemble spread of deterministic field) will fail.
       if ( not np.all(fld == 0 ) ):  #  Note:  I THINK THEY ARE ALL ZEROS -- NOT MASKED.
           cplot.bin_pcolormesh(lon_bin, lat_bin, fld, title=title, levels=LEVS, ddeg=DELTA, outfile=outfile, obar='horizontal')
   return

def plot_diff_field(bin1, bin2, drop=[], titpre='', outpre='PLOTS/', LEVS = np.arange(-0.1, 0.11, 0.02)):
   if ( isinstance(bin1, list) or isinstance(bin1,tuple) ): 
       for ibin, ibin1 in enumerate(bin1):
           iibin1=bin1[ibin]
           iibin2=bin2[ibin]
           plot_diff_field(iibin1, iibin2, drop=drop, outpre=outpre, LEVS=LEVS)
       return
   binP1 = bin1.copy()
   binP2 = bin2.copy()
   for idrop in drop:
       if ( idrop in binP1.keys() ): binP1.drop([idrop], axis=1, inplace=True)
       if ( idrop in binP2.keys() ): binP2.drop([idrop], axis=1, inplace=True)

   bkeys = list(binP1.keys())
   try:
       bkeys.remove('lon_bin')
   except:
       pass
   try:
       bkeys.remove('lat_bin')   
   except:
       pass
   print('Diff Field', outpre, bkeys)   
   for vari in bkeys:
       fld1 = binP1.loc[:, [vari, 'lon_bin', 'lat_bin']]
       fld2 = binP2.loc[:, [vari, 'lon_bin', 'lat_bin']]
       if ( ( vari[0:6] == 'sqrerr' ) or ( vari[0:6] == 'ensvar' ) ):
           fld1.loc[:, vari] = np.sqrt(fld1.loc[:, vari].values)
           fld2.loc[:, vari] = np.sqrt(fld2.loc[:, vari].values)
       fldd = fld1.merge(fld2, on=['lon_bin', 'lat_bin']).eval(vari+'= '+vari+'_x'+' - '+vari+'_y').drop([vari+'_x', vari+'_y'], axis=1)
       lon_bin = fldd.loc[:, 'lon_bin'].values  # DONT ASSUME SAME LAT/LONS
       lat_bin = fldd.loc[:, 'lat_bin'].values  # DONT ASSUME SAME LAT/LONS
       fldd_values = fldd.loc[:, vari].values
       varn = vari
       if ( vari[0:6] == 'sqrerr' ):
           varn='rmse'
       if ( vari[0:6] == 'ensvar' ):
           varn='estd'
       cmap = cmap_posd
       print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn+' difference'
       outfile=outpre+varn+'.png'
       # Attempting to plot zero fields (like ensemble spread of deterministic field) will fail.
       if ( not np.all(fldd_values == 0 ) ):  #  Note:  I THINK THEY ARE ALL ZEROS -- NOT MASKED.
           cplot.bin_pcolormesh(lon_bin, lat_bin, fldd_values, title=title, levels=LEVS, ddeg=DELTA, outfile=outfile, obar='horizontal')
   return

def plot_time_vars(dates, t_lists, labels, outdir, areanam, outdirpre=''):
    
    datestr1 = check_date.check_date(dates[0], dtlen=8)
    datestr2 = check_date.check_date(dates[-1], dtlen=8)
    datestrr = datestr1 + '_' + datestr2
    
    Vars = t_lists[0][0].keys()
    
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    colors = ['r', 'b', 'g', 'c', 'm']
    for var in Vars:
      outdire=ourdirpre+'_'+outdir+'/'
      outfile=outdire+'tseries_'+datestrr+'_'+areanam+'_'+varnam
      fig, axe = plt.subplots()
      axe.xaxis.set_major_locator(locator)
      axe.xaxis.set_major_formatter(formatter)
      for i_list, t_list in enumerate(t_lists):
        color=colors[i_list%5]
        tseries = [itime[var] for itime in t_list]
        axe.plot(dates, tseries, color=color, label=labels(i_list))
      axe.legend
      fig.savefig(outfile+'.png')
      fig.savefig(outfile+'.pdf')
     
    return
    
    
#DONT DO HERE   
#print("READ in ENSEMBLE")
#df_EnSSH = read_ensemble_SSH('GIOPS_T', 20220601, mp_read=False)
#print("CALCULATE ERRORS")
#gl_series, rgs_series, bin_series = calc_errors_date(20220601, 'GIOPS_T', ens=list(range(21)), deterministic=False, ddir=get_mdir(5), mp_read=False)    
