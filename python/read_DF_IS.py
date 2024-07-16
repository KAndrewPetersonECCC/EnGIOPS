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
import matplotlib.cm as cm
import subprocess
import traceback

import ola_functions
import read_DF_VP
from read_DF_VP import get_mdir
import check_date
import inside_polygon
import nearest
import cplot
import copy

import ensemble_functions
import rank_histogram
import create_pdf

num_cpus = len(os.sched_getaffinity(0))
intconvfac=10000.0
test_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'
if not os.path.isfile(test_file):
    print("WARNING: TEST FILE NOT PRESENT")

cmap_anom = copy.copy(cm.seismic)
cmap_anom.set_bad('grey', 1.0)

cmap_zero = copy.copy(cm.RdYlBu_r)
cmap_zero.set_bad('grey', 1.0)

cmap_posd = copy.copy(cm.viridis_r)
cmap_posd.set_bad('grey', 1.0)

cmap_ones = copy.copy(cm.hsv)


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
    time0 = time.time()
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt', 'TrackNum'], as_index='False')[['obs', 'mod', 'ana', 'misfit', 'oerr']]
    df_CNT = df_SSH.count()
    LT = len(df_CNT[df_CNT['misfit'] < count ])     
    print('Number of SubEnsembles = ', LT)    
    NT = len(df_CNT[df_CNT['misfit'] > count ])
    if ( NT > 0 ):
        print("WARNING:  Too many Ensemble Members")
        print(NT)
    df_EaSSH = df_SSH.mean()
    df_varSSH = df_SSH.var(ddof=0).rename(columns={'misfit':'ensvar', 'obs': 'varobs', 'mod' : 'varmod', 'ana' : 'varana'})
    df_EaSSH = pd.concat([df_EaSSH, df_varSSH[['ensvar', 'varobs', 'varmod', 'varana']]], axis=1).reset_index()
    return df_EaSSH

def add_squared_error(df_SSH):
    df_NU = df_SSH.copy() 
    misfit = df_SSH['misfit'].to_numpy()
    sqrerr = np.square(misfit)
    df_NU['sqrerr'] = sqrerr
    return df_NU

def add_adjust_error(df_SSH):
    df_NU = df_SSH.copy() 
    sqrerr = df_SSH['sqrerr'].to_numpy()
    obserr = df_SSH['oerr'].to_numpy()
    adjerr = sqrerr - np.square(obserr)
    df_NU['adjerr'] = adjerr
    return df_NU

def add_crps_SSH(df_EaSSH, df_EnSSH):
    df_crps = calc_crps_SSH(df_EnSSH)
    df_NU = pd.concat([df_EaSSH, df_crps['crps']],axis=1)
    return df_NU
        
def add_rank_SSH(df_EaSSH, df_EnSSH, nens=21):
    df_rank = calc_rank_SSH(df_EnSSH, nens=nens)
    df_NU = pd.concat([df_EaSSH, df_rank[['rank', 'size']]],axis=1)
    #print(df_NU.keys())
    return df_NU

def calc_crps_SSH(df_EnSSH):
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['misfit']]
    df_crps = df_SSH.apply(lambda x: read_DF_VP.calc_crps(x.to_numpy().flatten(),0)).rename('crps').reset_index()
    return df_crps

    
def calc_crps_SSHf(df_EnSSH):
    df_SSH = df_EnSSH.groupby(['Lat', 'Lon', 'tt'], as_index='False')[['obs', 'mod']]
    df_crps = df_SSH.apply(lambda x: read_DF_VP.calc_crps(x['mod'].to_numpy().flatten(), x['obs'].mean())).rename('crps').reset_index()
    return df_crps

def calc_rank_SSH(df_EnSSH, nens=21):
    df_rank = ensemble_functions.dataframe_rank( df_EnSSH, 'misfit', ['Lat', 'Lon', 'tt'], ncount=nens, rmsub=False)
    return df_rank
    
def sum_rank(df_EaSSH, nens=21):
    #print(df_EaSSH.keys())
    df_rank = df_EaSSH[['rank', 'size']]
    df_esub = df_rank[df_rank['size'] == nens ]
    df_hist = ensemble_functions.dataframe_hist( df_esub, ncount=nens)
    df_sumh = df_hist[['hist']].sum()   # Note the ['hist'] : Keeps it a dataframe.  Sum() reduces it to series.
    count = df_esub['rank'].count()
    df_sumh['hcount'] = count
    #print(df_sumh, type(df_sumh))
    return df_sumh

def calc_errors_date(date, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5), mp_read=True, SAT='ALL'):
    #mp_read = not mp   #  Need to find out how to run a child mp process inside another mp process.
    time0 = time.time()
    print('ENTERING CALC ERRORS for date', date, time.strftime("%Y%m%d--%H:%M:%S", time.gmtime()))
    if ( deterministic ):
        df_EnSSH = read_deterministic_SSH(expt, date, ddir=ddir, SAT=SAT)
        nens=1
    else:
        df_EnSSH = read_ensemble_SSH(expt, date, ddir=ddir, ens=ens, mp_read=mp_read, SAT=SAT)
        nens=len(ens)
    df_EaSSH = ensemble_average_SSH(df_EnSSH, count=nens)
    df_EaSSH = add_squared_error(df_EaSSH)
    df_EaSSH = add_adjust_error(df_EaSSH)
    df_EaSSH = add_crps_SSH(df_EaSSH, df_EnSSH)
    df_EaSSH = add_rank_SSH(df_EaSSH, df_EnSSH, nens=nens)
    gl_df =summed_field(df_EaSSH)
    hist_df = sum_rank(df_EaSSH, nens=nens)
    rgs_df = calc_region_errors(df_EaSSH)
    bin_df = sum_ongrid(df_EaSSH)
    pdf_df = calc_pdf(df_EnSSH[['misfit']])   # calc_pdf(df_column, brange=def_brange_err, Nbins=Nbins_PDF):
    pd2_ls = calc_2dpdf(df_EaSSH, var_err='misfit', var_spr='ensvar') # calc_2dpdf(df_column, var_err='misfit', var_spr='ensvar', brange_err=[-5,5], brange_spr=[0,5], Nbins=100)
    time1 = time.time()
    print('EXITING CALC ERRORS for expt/date', expt, date, time1-time0, time.strftime("%Y%m%d--%H:%M:%S", time.gmtime()), flush=True)
    
    return gl_df, rgs_df, bin_df, hist_df, pdf_df, pd2_ls
    

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
        points_are_inside = inside_polygon.test_inside_xyarray(polygon, df_EaSSH['Lon'].to_numpy(), df_EaSSH['Lat'].to_numpy())[0]
        df_region = df_EaSSH[points_are_inside]
        rg_series = summed_field(df_region)
        rgs_series.append(rg_series)
    return rgs_series


DELTA=1.0
def put_ongrid(df, delta=DELTA, latlon=['Lat', 'Lon']):
    df_g = df.copy()
    nomlat, nomlon = latlon
    bins_lons, bins_lats, xlon, xlat, query_lon, query_lat = read_DF_VP.nearest.grid(delta=delta)
    df_g['lat_bin'] = nearest.nearest3(query_lat, bins_lats, df[nomlat].to_numpy())
    df_g['lon_bin'] = nearest.nearest3(query_lon, bins_lons, df[nomlon].to_numpy())
    df_g.drop(latlon,axis=1)
    return df_g


ll_bin = ['lon_bin', 'lat_bin']     
def sum_ongrid(df_EaSSH, delta=DELTA):
    df_g = put_ongrid(df_EaSSH, delta=delta)   
    df_sum = df_g.groupby(['lon_bin', 'lat_bin']).sum().reset_index()
    df_cnt = df_g.groupby(['lon_bin', 'lat_bin']).count().reset_index()
    df_sup = pd.concat([df_sum, df_cnt['misfit'].rename('count')],axis=1)
    return df_sup


Nbins_PDF = 100
def_brange_err = [-1,1]
def_brange_spr = [0, 1]  
def init_pdf(brange, vars, Nbins=Nbins_PDF):
    # REALLY ONLY WORKS FOR GROUP OF ZERO CENTERED FIELDS? 
    time0 = time.time()
    bin_edge = create_pdf.init_bins(brange, Nbins)
    bin_mids = create_pdf.calc_bin_mid(bin_edge)
    binned_field = read_DF_VP.init_df()
    bins = create_pdf.zero_bins(bin_edge)
    #binned_field['bins'] = bin_mids
    for var in vars:
        binned_field = pd.concat([binned_field, pd.DataFrame(data={var: bins.copy()})])
    if ( isinstance(binned_field, pd.core.series.Series) ): binned_field=binned_field.to_frame()
    return binned_field, bin_edge

def calc_pdf(df_column, brange=def_brange_err, Nbins=Nbins_PDF):
    time0 = time.time()
    bin_keys = df_column.keys()
    binned_field, bin_edge = init_pdf(brange, bin_keys, Nbins=Nbins)
    print('LEN', len(binned_field), len(bin_edge))
    bin_mids = create_pdf.calc_bin_mid(bin_edge)
    binned_field['bins'] = bin_mids
    for ibin, bin_key in enumerate(bin_keys):
        tobin = df_column[bin_key].to_numpy()
        bina, nadd = create_pdf.bin_values(tobin, bin_edge)
        if ( ibin == 0 ): 
            nadd_zero = nadd
        else:
            if ( nadd != nadd_zero ):  print("WARNING:  DIFFERING data size??")
        binned_field[bin_key] = bina
    binned_field['count'] = nadd_zero
    return binned_field
        
def init2d_pdf(brange_err=def_brange_err, brange_spr=def_brange_spr, Nbins=Nbins_PDF):
    # REALLY ONLY WORKS FOR GROUP OF ZERO CENTERED FIELDS? 
    bin_edge_err = create_pdf.init_bins(brange_err, 2*Nbins)
    bin_edge_spr = create_pdf.init_bins(brange_err, Nbins)
    binned_field = read_DF_VP.init_df()
    bins = create_pdf.zero_2Dbins(bin_edge_err, bin_edge_spr)
    binned_field = [bins.copy(), 0]
    return binned_field, bin_edge_err, bin_edge_spr
    
def calc_2dpdf(df_column, var_err='misfit', var_spr='ensvar', brange_err=def_brange_err, brange_spr=def_brange_spr, Nbins=Nbins_PDF):
    misfit = df_column[var_err].to_numpy()
    spread = np.sqrt(df_column[var_spr].to_numpy())
    # binned_field is a list
    binned_field, bin_edge_err, bin_edge_spr = init2d_pdf(brange_err, brange_spr, Nbins)
    # binned_field is a list 
    binned_field = create_pdf.bin2D_values(misfit, spread,  bin_edge_err, bin_edge_spr)
    return binned_field  # Note binned_field is actually a tuple (binned_field, nadd)

def init_dataframes():
    gl_series = read_DF_VP.init_df()
    bin_series = read_DF_VP.init_df()
    hist_series = read_DF_VP.init_df()
    rgs_series = []
    for region in  read_DF_VP.PAREAS.keys():
        rg_sup = read_DF_VP.init_df()
        rgs_series.append(rg_sup)
    return gl_series, rgs_series, bin_series, hist_series

def cycle_thru_dates(dates, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5),  mp_date=True,  mp_read=False, SAT='ALL', NP=20):
    print('ENTERING CYCLE THRU DATES', 'mp_date='+str(mp_date), 'mp_read='+str(mp_read), flush=True)
    gl_series, rgs_series, bin_series, hist_series = init_dataframes()
    pdf_series, bin_edge = init_pdf( def_brange_err, ['misfit'], Nbins_PDF)
    print('PDF INIT', pdf_series['misfit'])
    pd2_series, bin_edge_err, bin_edge_spr = init2d_pdf(def_brange_err, def_brange_spr, Nbins_PDF)
    SSHvars = ['obs', 'mod', 'ana', 'oerr', 'misfit', 'sqrerr', 'adjerr', 'crps', 'ensvar', 'varobs', 'varmod', 'varana', 'count']
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
       add_gl_series, add_rgs_series, add_bin_series, add_hist_series, add_pdf_series, add_pd2_series = ADD_RESULTS[idate]
       OLD = ( gl_series, rgs_series, bin_series, hist_series, pdf_series, pd2_series )
       ADD = (add_gl_series, add_rgs_series, add_bin_series, add_hist_series, add_pdf_series, add_pd2_series)
       gl_series, rgs_series, bin_series, hist_series, pdf_series, pd2_series = addto_sums( OLD, ADD )
       day_gl_series, day_rgs_series = apply_averaging(add_gl_series, add_rgs_series)
       tglrs_series = addto_tlist(idate, tglrs_series, [day_gl_series]+day_rgs_series, SSHvars)

    # Apply Final Averaging on area averages
    gl_series_avg, rgs_series_avg = apply_averaging(gl_series, rgs_series, count_name='count', coord_list=SSHaxis)
    hist_series_avg = final_mean(hist_series, 'hcount', coord_list=[])
    # CHECK
    print( 'HISTOGRAM NORM', np.sum(hist_series_avg['hist'].to_numpy()[0]))
    print( 'HISTOGRAM', hist_series_avg['hist'].to_numpy()[0])
    print( 'HISTOGRAM TYPE', type( hist_series_avg['hist'].to_numpy()[0]))
    print( 'HISTOGRAM SHAPE', hist_series_avg['hist'].to_numpy()[0].shape)
    pdf_series_avg = final_mean(pdf_series, 'count', coord_list=['bins'])
    print('PDF FINAL', pdf_series_avg['misfit'])
    pd2_series_avg = pd2_series[0]/pd2_series[1]
    print('1 == PDF2 SUM = ', np.sum(pd2_series_avg) )
    print('PDF2 row', np.sum(pd2_series_avg, axis=0) )
    print('PDF2 col', np.sum(pd2_series_avg, axis=1) )
    IMAX = np.where( pd2_series_avg == np.max(pd2_series_avg) )
    IALL = np.where( pd2_series_avg != np.max(pd2_series_avg) )
    print('PDF2 off', np.sum(pd2_series_avg[IALL]), np.max(pd2_series_avg[IALL]), np.min(pd2_series_avg[IALL]))
    #pd2_series_avg = final_mean(pd2_series, 'count', coord_list=[])
    
    # Subset bin_series to Levels
    bin_series_avg = apply_bin_averaging(bin_series, count_name='count', llvars=['lon_bin', 'lat_bin'], extra=['tt'])
    bin_series_avg = add_ratio(bin_series_avg)
    tglrs_series = add_ratio(tglrs_series)
    print("FINAL DATE TIME", time.time() - time00, flush=True)
    return gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series, hist_series_avg, pdf_series_avg, pd2_series_avg

def add_ratio(df):
    if ( isinstance(df, list) ):
      if ( isinstance(df[0], pd.core.frame.DataFrame) or isinstance(df[0], pd.core.series.Series) or isinstance(df[0], list) ):
        df_list = []
        for dfe in df:
            dfn = add_ratio(dfe)
            df_list.append(dfn)
        return df_list
    if ( isinstance(df, pd.core.frame.DataFrame) ):
        oberr = np.square(df['oerr'].to_numpy())
        sqerr = df['sqrerr'].to_numpy()
        envar = df['ensvar'].to_numpy()
        lwerr = sqerr - oberr
        upvar = envar + oberr
    elif ( isinstance(df, pd.core.series.Series) ):
        oberr = np.square(df['oerr'])
        sqerr = df['sqrerr']
        envar = df['ensvar']
        lwerr = sqerr - oberr
        upvar = envar + oberr
    else:
        print('UNKNOWN', type(df))
        # Do Nothing for Now
        return df
    if ( isinstance(lwerr, np.ndarray) ):
        #lwerr[ np.where(lwerr < 0 ) ] = 0.0
        ipos = np.where(envar > 0 )
        ipps = np.where(upvar > 0 )
        imin = np.where(lwerr < 0 )
        ratir = np.ones(envar.shape)
        ratio = np.ones(envar.shape)
        ratip = np.ones(envar.shape)
        if ( len(ipos[0]) > 0 ):  ratir[ipos] = np.sqrt(sqerr[ipos] / envar[ipos])
        if ( len(ipos[0]) > 0 ):  ratio[ipos] = np.sqrt(lwerr[ipos] / envar[ipos])
        if ( len(ipps[0]) > 0 ):  ratip[ipps] = np.sqrt(sqerr[ipps] / upvar[ipps])
    elif ( isinstance(lwerr, np.float64) ):
        #if ( lwerr < 0 ): lwerr = 0
        ratir = 0.0
        ratio = 0.0
        ratip = 0.0
        if ( envar > 0 ):  ratir = np.sqrt(sqerr / envar)
        if ( envar > 0 ):  ratio = np.sqrt(lwerr / envar)
        if ( upvar > 0 ):  ratip = np.sqrt(sqerr / upvar)
    
    df['ratir'] = ratir
    df['ratio'] = ratio
    df['ratip'] = ratip
    return df
    
def series_to_df(df_series):
    df_frame = read_DF_VP.init_df()
    for key in df_series.keys():
        df_frame[key] = [df_series[key]]
    return df_frame

def addto_df( df_old, df_add):
    if ( isinstance(df_old, list) or isinstance(df_old, tuple) ):
        df_new = []
        for ilist, dfdf_old in enumerate(df_old):
            dfdf_add = df_add[ilist]
            dfdf_new = addto_df(dfdf_old, dfdf_add)
            df_new.append(dfdf_new)
        return df_new
    if ( isinstance(df_add, pd.core.series.Series) ): df_add = series_to_df(df_add)
    df_sum = pd.concat([df_old, df_add], axis=0).sum(axis=0)
    df_new = series_to_df(df_sum)
    print('ADDTO_DF', df_new)
    print('ADDTO_DF', type(df_new), type(df_sum))
    if ( isinstance(df_new, pd.core.frame.DataFrame) or isinstance(df_new, pd.core.series.Series) ): print('ADDTO_DF', df_new.keys())
    return df_new
    
def addto_sums( old_sums, add_sums):
    # Not sure why I want a module to do this.
    #
    gl_series, rgs_series, bin_series, hist_series, pdf_series, pd2_series = old_sums
    add_gl_series, add_rgs_series, add_bin_series, add_hist_series, add_pdf_series, add_pd2_series = add_sums
    
    # A TUPLE of one NUMPY ARRAY and one integer IS HANDLED ONE WAY
    pd2_new = [ pd2_series[ii] + add_pd2_series[ii] for ii in range(len(pd2_series)) ] 

    # DATAFRAMES NEED TO BE HANDLED ANOTHER WAY
    (gl_new, hist_new) = addto_df((gl_series, hist_series), (add_gl_series, add_hist_series))
    
    # AND A LIST OF DATAFRAMES YET ANOTHER WAY            
    new_rgs_series = []
    new_rgs_series = addto_df(rgs_series, add_rgs_series)
        
    # AND A BINNED DATAFRAME STILL ANOTHER WAY.         
    gr_cat = pd.concat([bin_series, add_bin_series])
    gr_new = gr_cat.groupby(['lat_bin', 'lon_bin']).sum().reset_index()

    # AND ANOTHER BINNED DATAFRAME STILL ANOTHER
    pdf_cat = pd.concat([pdf_series, add_pdf_series])
    pdf_new = pdf_cat.groupby(['bins']).sum().reset_index()
    print('PDF ADD', pdf_new)

    print("ADDTO SUMS TYPES", type(gl_new), type(new_rgs_series), type(new_rgs_series[0]), type(gl_new), type(hist_new), type(pdf_new), type(pd2_new))
        
    return gl_new, new_rgs_series, gr_new, hist_new, pdf_new, pd2_new


def final_mean( df_sum, count_name, coord_list ):
   df_avg = df_sum.copy()
   keys = df_avg.keys()
   #print('FINAL MEAN KEYS', keys, type(df_sum))
   for akey in coord_list:
       if ( akey in keys ):
           keys = keys.drop(akey)
   
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
    gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series, hist_series_avg, pdf_series_avg, pd2_series_avg = cycle_thru_dates(dates, expt, ens=ens, deterministic=deterministic, ddir=this_ddir, mp_read=mp_read_pass, mp_date=mp_date, SAT=SAT, NP=NP)
    return  expt, gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series, hist_series_avg, pdf_series_avg, pd2_series_avg
     

def cycle_thru_expts(dates, expts, enss, ddir=get_mdir(5), mp_expt=False, mp_read=False, mp_date=True, SAT='ALL', NP=20):

    print( "MP SETTINGS", mp_expt, mp_date, mp_read, flush=True)

    gl_list = []
    rgs_list = []
    bin_list = []
    tglrs_list = []
    expt_list = []
    hist_list = []
    pdf_list = []
    pd2_list = []
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
            expt_rtn, gl_series, rgs_series, bin_series, tglrs, hist_series, pdf_series, pd2_series = process_expt(dates, expt, ens_passed, dir_passed, mp_read=mp_read, mp_date=mp_date, SAT=SAT, NP=NP)
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            tglrs_list.append(tglrs)
            hist_list.append(hist_series)
            pdf_list.append(pdf_series)
            pd2_list.append(pd2_series)
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
            expt_rtn, gl_series, rgs_series, bin_series, tglrs, hist_series, pdf_series, pd2_series = fin_element
            if ( expt_rtn != expts[isort] ):
                print("WARNING: Experiments order not conserved!!")
                print(isort, expt_rtn, expts[isort])
            sort_list.append(expts.index(expt_rtn))
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            tglrs_list.append(tglrs)
            hist_list.append(hist_series)
            pdf_list.append(pdf_series)
            pd2_list.append(pd2_series)
            expt_list.append(expt_rtn)
        expt_copy = expt_list.copy()
        expt_list = [ expt_list[isort] for isort in sort_list ]
        gl_list = [ gl_list[isort] for isort in sort_list ]
        rgs_list = [ rgs_list[isort] for isort in sort_list ]
        bin_list = [ bin_list[isort] for isort in sort_list ]
        tgrgs_list = [ tgrgs_list[isort] for isort in sort_list ]
        hist_list = [ hist_list[isort] for isort in sort_list ]
        pdf_list = [ pdf_list[isort] for isort in sort_list ]
        pd2_list = [ pd2_list[isort] for isort in sort_list ]
        
        print("SORTED ", ( list(expt_list) == list(expts) ), expt_list, expts, sort_list, expt_copy )
    time1 = time.time()
    print( 'Total cycle_thur_expts Processing time ', 'ALL EXPTS', time1-time00, flush=True)
    return gl_list, rgs_list, bin_list, tglrs_list, hist_list, pdf_list, pd2_list

def produce_stats_plot( date_range, expts, enss, labels=None, outdir=None, ddir=get_mdir(5), mp_expt=False, mp_date=False, mp_read=False, outdirpre='', noensstat=False, SAT='ALL', NP=20, LEV_posd=None, LEV_anom=None, LEV_diff=None, LEV_ansq=None):
    SSHvars = ['obs', 'mod', 'ana', 'oerr', 'misfit', 'sqrerr', 'adjerr', 'crps', 'ensvar', 'varobs', 'varmod', 'varana', 'count']
    dropvar = ['obs', 'ana', 'varobs', 'varmod', 'varana']
    SSHpass = [ var for var in SSHvars if var not in dropvar ]
    SSHvarswant = ['count', 'misfit', 'sqrerr', 'adjerr', 'ensvar', 'crps', 'mod', 'oerr']
    SSHvarslist = SSHvarswant+['lon_bin', 'lat_bin']
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
    gl_list, rgs_list, bin_list, tglrs_list, hist_list, pdf_list, pd2_list = cycle_thru_expts(dates, expts, enss, ddir=ddir, mp_expt=mp_expt, mp_read=mp_read, mp_date=mp_date, SAT=SAT, NP=NP)
    print("FINISHED CYCLE THROUGH ALL EXPERIMENT DATES")

    nexpt=len(expts)
    for iexpt, expt in enumerate(expts):
        binL = bin_list[iexpt][SSHvarslist+['ratir', 'ratio', 'ratip']]
        hisL = hist_list[iexpt]['hist']
        pdfL = pdf_list[iexpt][['misfit']]
        pd2L = pd2_list[iexpt]
        outpreoutb=outdirpre+outdir[iexpt]+'/'+'SLA_'+datestrr+'_'
        titpre=labels[iexpt]+' '+datestrr
        print('TITLE', titpre, len(titpre))
        plot_df_field(binL, titpre=titpre, outpre=outpreoutb, drop=dropvar, LEV_posd=LEV_posd, LEV_anom=LEV_anom, LEV_ansq=LEV_ansq)
        outpreoutb=outdirpre+outdir[iexpt]+'/'+'SLA_'+datestrr+'_'+'rank'
        print('PLOT RANK', type(hisL))
        print('PLOT RANK', hisL)
        print('PLOT RANK', hisL.shape)
        print('PLOT RANK', hisL[0].shape)
        try: 
            hisL.to_numpy()
        except:
            print("PLOT RANK: TO NUMPY FAIL")
            
        plot_rank_hist(hisL, titpre, outpreoutb) 
        outpreoutb=outdirpre+outdir[iexpt]+'/'+'SLA_'+datestrr+'_'+'pdf'
        print('PLOT_PDF', type(pdfL))
        print('PLOT PDF', pdfL)
        print('PLOT PDF', pdfL.shape)
        try: 
            print('PLOT PDF', type(pdfL[0,0]))
            print('PLOT PDF', pdfL[0,0].shape)
        except:
            pass
        try:
            # PDF IS zero dimensoinal?  GROUPY_BY????
            plot_pdf(pdfL[0,0], titpre, outpreoutb) 
        except:
            print(traceback.print_exc())
        outpreoutb=outdirpre+outdir[iexpt]+'/'+'SLA_'+datestrr+'_'+'PDF'
        plot_2dpdf(pd2L, titpre, outpreoutb) 
        print("FINISHED FULL FIELD SLA : ", labels[iexpt])
        if ( iexpt == 0 ): 
            bin0=binL
        else:
            odir=outdirpre+outdir[0]+'_'+outdir[iexpt]
            titpre=labels[0]+'-'+labels[iexpt]+' '+datestrr
            print('TITLE', titpre, len(titpre))
            outpreoutb=odir+'/'+'SLA_'+datestrr+'_'
            plot_diff_field(bin0, binL, titpre=titpre, outpre=outpreoutb, drop=dropvar+['oerr'], LEVS=LEV_diff)
            print("FINISHED DIFF FIELD SLA : ", labels[iexpt])
    print("FINISHED SLA PLOTS")

    narea = len(tglrs_list[0])
    areanams = ['global']+list(read_DF_VP.PAREAS.keys())
    narea = len(areanams)
    for iarea in range(narea):
        tx_list = []
        for iexpt in range(nexpt):
            tglrs = tglrs_list[iexpt][iarea]
            tt_list = []
            for it, a_tglrs in enumerate(tglrs):
                aa_tglrs = a_tglrs[SSHvarswant]
                tt_list.append(aa_tglrs)
            tx_list.append(tt_list)
            
        print(tx_list[0][0].keys())
        outdire=outdirpre+outdir[0]+'/'
        plot_time_vars(dates, tx_list, labels, outdire, areanams[iarea])
    print("FINISHED TIMESERIES PLOTS")

    return

def plot_rank_hist(np_hist, title, pfile):
    print('PLOT RANK HIST', type(np_hist))
    if ( isinstance(np_hist, np.ndarray) ): pass
    if ( isinstance(np_hist, pd.core.series.Series) ): np_hist=np_hist[0]
    if ( pfile.endswith(".png") or pfile.endswith(".pdf") ): pfile=pfile[:-4]
    rank_histogram.plot_histogram(np_hist, title, pfile)
    return
    
def plot_pdf(df_pdf, title, pfile):
    if ( pfile.endswith(".png") or pfile.endswith(".pdf") ): pfile=pfile[:-4]
    __, bin_edge = init_pdf(def_brange_err, ['misfit'])
    create_pdf.plot_pdf(bin_edge, df_pdf['misfit'], title, pfile)
    return
    
def plot_2dpdf(np_pdf, title, pfile, levels=np.arange(0,0.2, 0.01), cmap=cmap_posd):
    if ( pfile.endswith(".png") or pfile.endswith(".pdf") ): pfile=pfile[:-4]
    __, bin_edge_err, bin_edge_spr = init2d_pdf()
    IPOS = np.where(np_pdf > 0 )
    ITEN = np.where(np_pdf > 0.1*np.max(np_pdf) )
    print("NP_PDF NUM", len(IPOS[0]))
    print("NP_PDF TEN", len(ITEN[0]))
    print("NP_PDF MAX", np.max(np_pdf))
    print("NP_PDF SUM", np.sum(np_pdf))
    create_pdf.plot_2dpdf(bin_edge_err, bin_edge_spr, np_pdf, title, pfile)
    return

def plot_df_field(binF, drop=[], outpre='PLOTS/', titpre='', LEV_posd=None, LEV_anom=None, LEV_ansq=None):
   if ( isinstance(binF, list) or isinstance(binF, tuple) ): 
       for ibinF in binF:
           plot_df_field(ibinF, drop=drop, outpre=outpre)
       return
   binP = binF.copy()
   lon_bin = binF['lon_bin'].to_numpy()  # lon_bin is now a Frame not Series
   lat_bin = binF['lat_bin'].to_numpy()
   binP.drop(['lon_bin', 'lat_bin'], inplace=True, axis=1)
   for idrop in drop:
       if ( idrop in binP.keys() ): binP.drop([idrop], axis=1, inplace=True)

   print('Full Field', outpre, list(binP.keys()))   
   for vari in binP.keys():
       fld = binF[vari].to_numpy()
       varn = vari
       LEVS = None
       cmap = cmap_posd
       amap = cmap_zero
       if ( vari[0:6] == 'sqrerr' ):
           fl2 = fld - np.square(binF['misfit'].to_numpy())
           fld=np.sqrt(fld)
           fl2=np.sqrt(fld)
           varn='rmse'
           var2='stde'
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
           if ( isinstance(LEV_posd, type(None)) ):
               LEV2 = read_DF_VP.find_good_contour_levels(fl2, posd=True)
           else:
               LEV2=LEV_posd
       if ( vari[0:6] == 'ensvar' ):
           fl2 = (binF['sqrerr'].to_numpy()) - np.square(binF['misfit'].to_numpy()) - fld
           fld = np.sqrt(fld)
           varn='estd'
           var2='drmse'
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
           if ( isinstance(LEV_ansq, type(None)) ):
               LEV2 = read_DF_VP.find_good_contour_levels(fl2, posd=False)
           else:
               LEV2=LEV_ansq
       if ( vari[0:6] == 'adjerr' ):
           fl2 = fld - np.square(binF['misfit'].to_numpy()) - (binF['ensvar'].to_numpy())
           ineg = np.where(fld < 0)
           fld[ineg] = 0.0
           ineg = np.where(fl2 < 0)
           #fl2[ineg] = 0.0
           fld=np.sqrt(fld)
           #fl2=np.sqrt(fl2)
           varn='armse'
           var2='brmse'
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
           if ( isinstance(LEV_ansq, type(None)) ):
               LEV2 = read_DF_VP.find_good_contour_levels(fl2, posd=False)
           else:
               LEV2=LEV_ansq
       if ( vari[0:4] == 'crps' ):
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
       if ( vari[0:6] == 'misfit' ):
           varn='merr'
           cmap=cmap_zero
           if ( isinstance(LEV_anom, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=False)
           else:
               LEVS=LEV_anom
       if ( vari[0:4] == 'oerr' ):
           varn=vari
           if ( isinstance(LEV_posd, type(None)) ):
               LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           else:
               LEVS=LEV_posd
       if ( vari[0:3] == 'mod' ):
           varn=vari
           LEVS = read_DF_VP.find_good_contour_levels(fld, posd=False)
       if ( vari[0:5] == 'ratir' ):
           varn=vari
           #LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           LEVS = np.array([0, 0.25, 0.33, 0.5, 2.0/3.00, 0.75, 1.00, 4.0/3.0, 3.0/2.0, 2.00, 3.00, 4.00]) 
           cmap = cmap_zero
       if ( vari[0:5] == 'ratio' ):
           varn=vari
           #LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           LEVS = np.array([0, 0.25, 0.33, 0.5, 2.0/3.00, 0.75, 1.00, 4.0/3.0, 3.0/2.0, 2.00, 3.00, 4.00]) 
           cmap = cmap_zero
       if ( vari[0:5] == 'ratip' ):
           varn=vari
           #LEVS = read_DF_VP.find_good_contour_levels(fld, posd=True)
           LEVS = np.array([0, 0.20, 0.25, 0.33, 0.5, 2.0/3.00, 0.75, 0.80, 5.0/6.00, 1.00, 1.20, 1.25, 4.0/3.0, 3.0/2.0, 2.00, 3.00, 4.00, 5.00, 100.0]) 
           cmap = cmap_zero
       outfile=outpre+varn+'.png'
       print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn
           if ( varn == 'armse' ): title='adjusted rmse'
       print(varn, 'Max/Min', np.max(fld), np.min(fld)) 
       # Attempting to plot zero fields (like ensemble spread of deterministic field) will fail.
       if ( not np.all(fld == 0 ) ):  #  Note:  I THINK THEY ARE ALL ZEROS -- NOT MASKED.
           print('PLOT', type(lon_bin), type(lat_bin), type(fld))
           print('PLOT', lon_bin.shape, lat_bin.shape, fld.shape)
           cplot.bin_pcolormesh(lon_bin, lat_bin, fld, ddeg=DELTA, title=title, levels=LEVS, outfile=outfile, obar='horizontal', cmap=cmap)
       if ( ( vari[0:6] == 'adjerr' ) or ( vari[0:6] == 'sqrerr' )  or ( vari[0:6] == 'ensvar' )):
           outfile=outpre+var2+'.png'
           dmap = amap
           if ( var2 == 'bmrse' ): cmap = amap
           if ( var2 == 'drmse' ): cmap = amap
           if ( var2 == 'stde' ): dmap = cmap
           print('TITLE', titpre, len(titpre))
           if ( len(titpre) > 0 ):
               title=titpre+' '+var2
               if ( var2 == 'brmse' ): title=titpre+' '+'squared errors difference'
               if ( var2 == 'drmse' ): title=titpre+' '+'squared errors difference'
           else:
               title=var2
               if ( var2 == 'brmse' ): title='squared errors difference'
               if ( var2 == 'drmse' ): title='squared errors difference'
           print(var2, 'Max/Min', np.max(fl2), np.min(fl2)) 
           # Attempting to plot zero fields (like ensemble spread of deterministic field) will fail.
           if ( not np.all(fl2 == 0 ) ):  #  Note:  I THINK THEY ARE ALL ZEROS -- NOT MASKED.
               print('PLOT', type(lon_bin), type(lat_bin), type(fld))
               print('PLOT', lon_bin.shape, lat_bin.shape, fld.shape)
               print('LEV', LEV2, len(LEV2))
               cplot.bin_pcolormesh(lon_bin, lat_bin, fl2, ddeg=DELTA, title=title, levels=LEV2, outfile=outfile, obar='horizontal', cmap=dmap)
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
       if ( ( vari[0:6] == 'sqrerr' ) or ( vari[0:6] == 'ensvar' ) or ( vari[0:6] == 'adjerr' ) ):
           fld1.loc[:, vari] = np.sqrt(fld1.loc[:, vari].to_numpy())
           fld2.loc[:, vari] = np.sqrt(fld2.loc[:, vari].to_numpy())
       fldd = fld1.merge(fld2, on=['lon_bin', 'lat_bin']).eval(vari+'= '+vari+'_x'+' - '+vari+'_y').drop([vari+'_x', vari+'_y'], axis=1)
       lon_bin = fldd.loc[:, 'lon_bin'].to_numpy()  # DONT ASSUME SAME LAT/LONS
       lat_bin = fldd.loc[:, 'lat_bin'].to_numpy()  # DONT ASSUME SAME LAT/LONS
       fldd_values = fldd.loc[:, vari].to_numpy()
       print('DIFF PLOT SHAPE', fldd_values.shape, lon_bin.shape, lat_bin.shape)
       varn = vari
       if ( vari[0:6] == 'sqrerr' ):
           varn='rmse'
       if ( vari[0:6] == 'adjerr' ):
           varn='armse'
       if ( vari[0:6] == 'ensvar' ):
           varn='estd'
       cmap = cmap_zero
       print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn+' difference'
           if ( varn == 'armse' ): title='adjusted rmse difference'
       outfile=outpre+varn+'.png'
       # Attempting to plot zero fields (like ensemble spread of deterministic field) will fail.
       if ( not np.all(fldd_values == 0 ) ):  #  Note:  I THINK THEY ARE ALL ZEROS -- NOT MASKED.
           cplot.bin_pcolormesh(lon_bin, lat_bin, fldd_values, ddeg=DELTA, title=title, levels=LEVS, outfile=outfile, obar='horizontal', cmap=cmap)
   return

def plot_time_vars(dates, t_lists, labels, outdir, areanam):
    
    datestr1 = check_date.check_date(dates[0], dtlen=8)
    datestr2 = check_date.check_date(dates[-1], dtlen=8)
    datestrr = datestr1 + '_' + datestr2
    
    Vars = t_lists[0][0].keys()
    
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    colors = ['r', 'b', 'g', 'c', 'm']
    for var in Vars:
      outfile=outdir+'/'+'tseries_'+datestrr+'_'+areanam+'_'+varnam
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
