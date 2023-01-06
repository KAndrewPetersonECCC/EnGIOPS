#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import datetime
import numpy as np
import pandas as pd
import pickle

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import subprocess

import ola_functions
import ensemble_functions
import cplot
import write_nc_grid
import find_common

import multiprocessing
from functools import partial

num_cpus = len(os.sched_getaffinity(0))
file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

site5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
site6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

dates = [20200304, 20200603, 20200902, 20201230]
ens_list = range(21)

#df_list_ssh = rank_histogram.read_IS_ensemble('GIOPS_T', 20220601, satellite='ALL', mp=True) 
#df_list_sst = rank_histogram.read_DS_ensemble('GIOPS_T', 20220601, night=True, mp=True) 

def check_date(date, outtype=str, dtlen=8):
    if ( (outtype==str) or (outtype==int) ):
      if ( isinstance(date, datetime.datetime) or isinstance(date, datetime.date) ):
        if ( dtlen == 8 ):  
          datestr=date.strftime("%Y%m%d")
        elif ( dtlen == 10 ): 
          datestr=date.strftime("%Y%m%d%H")
        elif ( dtlen == 12 ): 
          datestr=date.strftime("%Y%m%d%H%M")
        elif ( dtlen == 14 ): 
          datestr=date.strftime("%Y%m%d%H%M%S")
        else:
          datestr=date.strftime("%Y%m%d")
      if ( isinstance(date, int) ):  datestr=str(date)
      if ( isinstance(date, str) ): datestr=date
      if ( len(datestr) < dtlen ):
          datestr=datestr+str(0).zfill(dtlen-len(datestr))
      if ( len(datestr) > dtlen ):
          datestr=datestr[:dtlen]
    if ( outtype ==int ): datestr=int(datestr)
    if ( outtype== datetime.datetime ):
      if ( isinstance(date, int) ): date=str(date)
      if ( isinstance(date, str) and ( len(date) == 8 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d')  
      elif ( isinstance(date, str) and ( len(date) == 10 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H')  
      elif ( isinstance(date, str) and ( len(date) == 12 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M')  
      elif ( isinstance(date, str) and ( len(date) == 14 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M%S')  
      if ( isinstance(date, datetime.datetime) ): datestr=date
      if ( isinstance(date, datetime.date) ): datestr=datetime.datetime(*date.timetuple()[:4])
    return datestr

file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

def subset_DF_LIST(DF_list, key_id, val):
    NF_LIST = []
    for DF in DF_list:
        df =  ola_functions.subset_df(DF, key_id, val)
        dfr = df.reset_index()
        NF_LIST.append(dfr)
    return NF_LIST
        
def read_DS_ensemble(expt, date, datadir=site5, enslist=ens_list, night=True, mp=True):
    date8 = check_date(date, dtlen=8)
    dated = check_date(date, dtlen=10)

    input_files = []
    nens=len(enslist)
    for ie in enslist:
       ensstr=str(ie)
       print(datadir, expt, ensstr,date8, dated)
       input_file=datadir+'/'+expt+ensstr+'/SAM2/'+date8+'/DIA/'+dated+'_SAM.ola' 
       input_files.append(input_file)

    if ( not mp ):
        DF_list = []
        for input_file in input_files:
            DS = ola_functions.SST_DAY_dataframe(input_file,NIGHT=night)
            DF_list.append(DS)
    else:
        nproc=min([num_cpus, nens])
        read_pool = multiprocessing.Pool(nproc)
        DF_list = read_pool.map(partial(ola_functions.SST_DAY_dataframe, NIGHT=night), input_files)
        read_pool.close()
        read_pool.join()
        
    return DF_list           
    
def read_IS_ensemble(expt, date, datadir=site5, enslist=ens_list, satellite='ALL', mp=True):
    date8 = check_date(date, dtlen=8)
    dated = check_date(date, dtlen=10)
    isat = 0
    if ( isinstance(satellite, int) ): 
        isat=satellite
        satellite=str(satellite)
    elif ( isinstance(satellite, type(None)) ):
        satellite='NONE'
    SAT = satellite.upper()

    input_files = []
    nens=len(enslist)
    for ie in enslist:
       ensstr=str(ie)
       print(datadir, expt, ensstr,date8, dated)
       input_file=datadir+'/'+expt+ensstr+'/SAM2/'+date8+'/DIA/'+dated+'_SAM.ola' 
       input_files.append(input_file)

    if ( not mp ):  
        DF_list = []
        for input_file in input_files:
            df_IS = ola_functions.SSH_SAT_dataframe(input_file, SAT=satellite)   
            DF_list.append(df_IS)
    else:
        nproc=min([num_cpus, nens])
        read_pool = multiprocessing.Pool(nproc)
        DF_list = read_pool.map(partial(ola_functions.SSH_SAT_dataframe, SAT=satellite), input_files)
        read_pool.close()
        read_pool.join()
    return DF_list

def rewrite_IS_ensemble(expt, date, datadir=site5, enslist=ens_list, satellite='ALL', mp=True):
    DF_list = read_IS_ensemble(expt, date, datadir=datadir, enslist=enslist, satellite=satellite, mp=mp)
    NF_list = find_common.find_common_by_Tstp(DF_list, mp=mp)
    
    filename=diredir+'/'+expt+'/'+'DRU2'+'/'+'OLA_IS.'+sdate+'.pkl'
    with open(filename,'wb') as fp:
        pickle.dump(NF_LIST,fp)
    
def rank(list):
    posn = [ ( value > 0 ) for value in list ]
    rank_val = sum(posn)
    return rank_val
    
def rank_DS_obs(DF_list):
    nobs = len(DF_list[0])
    rank_np = np.zeros(nobs)
    hist_np = np.zeros(len(DF_list)+1)
    for iobs in range(nobs):
        list = [ DF['misfit'].values[iobs] for DF in DF_list ]
        rank_vl = rank(list)
        rank_np[iobs] = rank_vl
        hist_np[rank_vl] = hist_np[rank_vl]+1
    return rank_np, hist_np

def rank_misfit(DF_list, unique=['Lon', 'Lat'], var='misfit'):
    df_rank = ensemble_functions.dataframe_rank( DF_list, var, unique)
    hist_np = ensemble_functions.histo_array(df_rank)
    return hist_np

def create_dates(date_start, date_final, date_inter):
    dates=[]
    date_start = check_date(date_start, outtype=datetime.datetime)
    date_final = check_date(date_final, outtype=datetime.datetime)
    
    date = date_start
    while ( date <= date_final ):
        dates.append(date)
        date = date + datetime.timedelta(days=date_inter)
    return dates
    
def rank_over_range(expt, dates, obstype='DS', enslist=ens_list, datadir=site5, groupby=True):
    nens=len(enslist)
    hist_sm = np.zeros(nens+1)
    for date in dates:
        # Not sure if this will be generalizable yet -- but leave option open.
        if ( obstype == 'DS' ):
            DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir)
        if ( obstype == 'IS' ):
            DF_list = read_IS_ensemble(expt, date, enslist=enslist, datadir=datadir)
        if ( groupby):
            hist_np = rank_misfit(DF_list, unique=['Lon', 'Lat'], var='misfit')
        else:
            rank_np, hist_np = rank_DS_obs(DF_list)
        hist_sm = hist_sm + hist_np
    return hist_sm

def plot_histogram(hist_np, title, pfile):
    if ( isinstance(hist_np, list) ): hist_np = np.array(hist_np).astype(float)
    fig=plt.figure()
    axe=plt.subplot()
    print("TYPE", type(hist_np), hist_np)
    norm_np = hist_np.astype(float) / float(sum(hist_np))
    xaxis = np.arange(len(hist_np)).astype(float)
    xaxis = xaxis - 0.5
    axe.bar(range(len(hist_np)), norm_np, width=1)
    axe.set_title(title)
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)
    return
    
def plot_histograms(hist_np_list, labels, title, pfile):
    fig=plt.figure()
    axe=plt.subplot()
    nh = len(hist_np_list)
    width=1.0 / nh
    xaxis = np.arange(len(hist_np_list[0])).astype(float)
    xaxis = xaxis - 0.5
    xaxis = xaxis + 0.5*width
    for ih, hist_np in enumerate(hist_np_list):
        if ( isinstance(hist_np, list) ): hist_np = np.array(hist_np).astype(float)
        norm_np = hist_np.astype(float) / float(sum(hist_np))
        axe.bar(xaxis, norm_np, width=1, label=labels[ih])
        xaxis = xaxis + width
    axe.set_title(title)
    axe.legend()
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)
    return
    
def plot_rank_over_range(odir, expt, date_range, obstype='DS', enn=21, datadir=site5, groupby=True):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    title='Rank Histogram over Period '+datestr0+'-'+datestr1
    pfile=odir+'/'+expt+'_'+datestrc+'.rhist'
    
    hist_sm = rank_over_range(expt, dates, obstype='DS', enslist=enslist, datadir=datadir, groupby=groupby)
    plot_histogram(hist_sm, title, pfile)
    return
    
def plot_ranks_over_range(oprefix, expts, date_range, labels=None, obstype='DS', enn=21, datadir=site5, groupby=True):
    print(expts)
    print(labels)
    print(None)
    print( isinstance(labels, type(None)))
    if ( isinstance(labels, type(None)) ): labels=expts
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    title='Rank Histogram over Period '+datestr0+'-'+datestr1
    pfile=oprefix+'_'+datestrc+'.rhist'
    hist_sm_list = []
    for expt in expts:    
        hist_sm = rank_over_range(expt, dates, obstype=obstype, enslist=enslist, datadir=datadir,groupby=groupby)
        hist_sm_list.append(hist_sm)
    plot_histograms(hist_sm_list, labels, title, pfile)
    return

def ensemble_mean_misfit(DF_list):
    misfit_list = [ DF['misfit'].values for DF in DF_list]
    misfit_mean = sum(misfit_list) / len(misfit_list)
    DF_mean = DF_list[0].copy()
    DF_mean['misfit'] = misfit_mean
    return DF_mean

def ensemble_vari_misfit(DF_list):
    misfit_list = [ DF['misfit'].values for DF in DF_list]
    misfit_mean = sum(misfit_list) / len(misfit_list)
    misfit_anom = [ ( misfit - misfit_mean ) for misfit in misfit_list]
    misfit_squa = [ misfit**2 for misfit in misfit_anom]
    misfit_vari = sum(misfit_squa) / len(misfit_squa) 
    nobs = len(misfit_mean)
    misfit_crps = np.zeros(misfit_mean.shape)
    for iv in range(nobs):
        ens = [ misfit[iv] for misfit in misfit_list]
        misfit_crps[iv] = ensemble_functions.calc_crps(ens, 0)
    DF_mean = DF_list[0].copy()
    DF_mean['misfit'] = misfit_mean
    DF_mean['errvar'] = misfit_vari
    DF_mean['crps'] = misfit_crps
    return DF_mean

def ensemble_vari_misfit_type(DF_list, obstype='IS'):
    unique = ['Lon', 'Lat', 'tt']
    vars = ['misfit']
    if ( type == 'IS' ): 
        unique = unique + []
    elif ( type == 'DS' ):
        unique = unique + [];
    
    df_ensm, df_evar = ensemble_functions.ens_mean( DF_list, vars, unique )
    df_evar.rename(columns={'misfit':'errvar'},inplace=True)
    df_crps = ensemble_functions.calc_crps_df_err(DF_list, unique, var='misfit')
    df_mean = pd.concat([ df_ensm, df_evar['errvar'], df_crps['crps'] ], axis=1)
    return df_mean
    
def bin_errors_init(ddeg=1):
    grid_lon, grid_lat, lon_bin, lat_bin, grid_sum, grid_cnt = cplot.make_bin_grid(ddeg=ddeg)
    bin_misfit , cnt_misfit = grid_sum.copy(), grid_cnt.copy()
    bin_squerr , cnt_sqrerr = grid_sum.copy(), grid_cnt.copy()
    bin_crps   , cnt_crps   = grid_sum.copy(), grid_cnt.copy()
    LLS=[grid_lon, grid_lat, lon_bin, lat_bin]
    BIN=[bin_misfit, bin_squerr, bin_crps, cnt_misfit, cnt_sqrerr, cnt_crps]
    return LLS, BIN
    
def add_DF_to_bin(DF, LLS, BIN):
    [grid_lon, grid_lat, lon_bin, lat_bin] = LLS
    [bin_misfit, bin_sqrerr, bin_crps, cnt_misfit, cnt_sqrerr, cnt_crps]=BIN[:]
    lon=DF['Lon'].values
    lat=DF['Lat'].values
    misfit = DF['misfit'].values
    sqrerr = misfit**2
    crps =  misfit**2
    bin_misfit , cnt_misfit = cplot.binfldsumcum(lon, lat, misfit, lon_bin, lat_bin, bin_misfit, cnt_misfit)
    bin_sqrerr , cnt_sqrerr = cplot.binfldsumcum(lon, lat, sqrerr, lon_bin, lat_bin, bin_sqrerr, cnt_sqrerr)
    bin_crps   , cnt_crps   = cplot.binfldsumcum(lon, lat, crps  , lon_bin, lat_bin, bin_crps  , cnt_crps)
    OBIN=[bin_misfit, bin_sqrerr, bin_crps, cnt_misfit, cnt_sqrerr, cnt_crps]
    return OBIN

def bin_error_over_ensemble(expt, date, obstype='IS', ID='ALL', enslist=ens_list, datadir=site5):
    LLS, BIN=bin_errors_init()
    [bin_misfit, bin_sqrerr, bin_crps, cnt_misfit, cnt_sqrerr, cnt_crps]=BIN[:]
    OBIN = [bin_misfit.copy(), bin_sqrerr.copy(), bin_crps.copy(), cnt_misfit.copy(), cnt_sqrerr.copy(), cnt_crps.copy()]
	
    if ( obstype=='DS' ):
        night=False
        if ( ID == 'night' ): 
            night=True
        DF_LIST = read_DS_ensemble(expt, date, datadir=datadir, enslist=ens_list, night=night)

    if ( obstype=='IS' ):
        DF_LIST = read_IS_ensemble(expt, date, datadir=datadir, enslist=ens_list, satellite=ID)

    OBIN_LIST=[]
    for DF in DF_LIST:
        OBIN = add_DF_to_bin(DF, LLS, OBIN)
        __, MBIN=bin_errors_init()
        OBIN_LIST.append(add_DF_to_bin(DF, LLS, MBIN))
        
    return LLS, OBIN, OBIN_LIST
    
def bin_errors_over_erange(expt, dates, obstype='IS', enslist=ens_list, datadir=site5):
    nens = len(enslist)
    LLS, SBIN=bin_errors_init()
    [grid_lon, grid_lat, lon_bin, lat_bin]=LLS
    [sbin_misfit, sbin_sqrerr, scnt_misfit, scnt_sqrerr]=SBIN[:]
    SBIN_LIST=[]
    for iens in range(nens):
        SBIN_LIST.append([sbin_misfit.copy(), sbin_sqrerr.copy(), scnt_misfit.copy(), scnt_sqrerr.copy()])
    for idate, date in enumerate(dates):
        __, OBIN, OBIN_LIST = bin_error_over_ensemble(expt, date, obstype=obstype, enslist=enslist, datadir=datadir)
        [bin_misfit, bin_sqrerr, cnt_misfit, cnt_sqrerr]=OBIN[:]
        [sbin_misfit, sbin_sqrerr, scnt_misfit, scnt_sqrerr]=SBIN[:]
        SBIN =  [sbin_misfit+bin_misfit, sbin_sqrerr+bin_sqrerr, scnt_misfit+cnt_misfit, scnt_sqrerr+cnt_sqrerr]
        for iens in range(nens):
            [bin_misfit, bin_sqrerr, cnt_misfit, cnt_sqrerr]=OBIN_LIST[iens][:]
            [sbin_misfit, sbin_sqrerr, scnt_misfit, scnt_sqrerr]=SBIN_LIST[iens][:]
            SBIN_LIST[iens] =  [sbin_misfit+bin_misfit, sbin_sqrerr+bin_sqrerr, scnt_misfit+cnt_misfit, scnt_sqrerr+cnt_sqrerr]
    
    [sbin_misfit, sbin_sqrerr, scnt_misfit, scnt_sqrerr]=SBIN[:]
    avg_misfit = cplot.binfldsumFIN(sbin_misfit, scnt_misfit)
    avg_tsqerr = cplot.binfldsumFIN(sbin_sqrerr, scnt_sqrerr)
    ERROR_LIST = []
    for iens in range(nens):
        [sbin_misfit, sbin_sqrerr, scnt_misfit, scnt_sqrerr]=SBIN_LIST[iens][:]
        mavg_misfit = cplot.binfldsumFIN(sbin_misfit, scnt_misfit)
        mavg_sqrerr = cplot.binfldsumFIN(sbin_sqrerr, scnt_sqrerr)
        mspa_sqrerr = mavg_sqrerr - mavg_misfit**2
        ERROR_LIST.append( (mavg_misfit, mavg_sqrerr, mspa_sqrerr, mavg_misfit-avg_misfit, mavg_sqrerr-avg_tsqerr, (mavg_misfit-avg_misfit)**2 ) )

    VARIA_LIST = average_list_with_list(ERROR_LIST)
    spa_sqrerr = VARIA_LIST[2]
    for ierror, error in enumerate(VARIA_LIST):
        print('ZERO', np.max(error), np.min(error))
    avg_errvar = avg_tsqerr - spa_sqrerr - avg_misfit**2
    avg_sqrerr = avg_tsqerr - avg_errvar 
    avg_crps   = avg_crps
    return avg_misfit, avg_sqrerr, avg_errvar, avg_tsqerr, avg_crps, [grid_lon, grid_lat]    
               
def average_list_with_list(LIST_LIST):
    AVG_LIST = []
    nelements = len(LIST_LIST[0])
    for ielement in range(nelements):
        sublist = [ listsub[ielement] for listsub in LIST_LIST ]
        AVG_LIST.append(sum(sublist) / len(sublist))
    return AVG_LIST
    
def bin_errors_over_range(expt, dates, obstype='DS', enslist=ens_list, datadir=site5, groupby=True):
    grid_lon, grid_lat, lon_bin, lat_bin, grid_sum, grid_cnt = cplot.make_bin_grid(ddeg=1)
    bin_misfit , cnt_misfit = grid_sum.copy(), grid_cnt.copy()
    bin_squerr , cnt_squerr = grid_sum.copy(), grid_cnt.copy()
    bin_errvar , cnt_errvar = grid_sum.copy(), grid_cnt.copy()
    bin_crps   , cnt_crps   = grid_sum.copy(), grid_cnt.copy()
    for date in dates:
        if ( obstype == 'DS' ):
            DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir, night=True, mp=True)
        elif ( obstype == 'IS' ):
            DF_list = read_IS_ensemble(expt, date, enslist=enslist, datadir=datadir, satellite='ALL', mp=True)
            
        if ( groupby == True ):
            DF_mean = ensemble_vari_misfit_type(DF_list, obstype=obstype)
        else:
            DF_mean = ensemble_vari_misfit(DF_list)
        lon = DF_mean['Lon'].values
        lat = DF_mean['Lat'].values
        misfit = DF_mean['misfit'].values
        squerr = misfit**2
        errvar = DF_mean['errvar'].values
        crps   = DF_mean['crps'].values
        bin_misfit , cnt_misfit = cplot.binfldsumcum(lon, lat, misfit, lon_bin, lat_bin, bin_misfit, cnt_misfit)
        bin_squerr , cnt_squerr = cplot.binfldsumcum(lon, lat, squerr, lon_bin, lat_bin, bin_squerr, cnt_squerr)
        bin_errvar , cnt_errvar = cplot.binfldsumcum(lon, lat, errvar, lon_bin, lat_bin, bin_errvar, cnt_errvar)
        bin_crps   , cnt_crps   = cplot.binfldsumcum(lon, lat, errvar, lon_bin, lat_bin, bin_crps, cnt_crps)
    tot_cnt_misfit = np.sum(cnt_misfit)
    tot_cnt_squerr = np.sum(cnt_squerr)
    tot_cnt_errvar = np.sum(cnt_errvar)
    tot_cnt_crps   = np.sum(cnt_crps)
    if ( tot_cnt_squerr != tot_cnt_misfit ): print('Warning, squerr/misfit cnt error', tot_cnt_misfit, tot_cnt_squerr)
    if ( tot_cnt_errvar != tot_cnt_misfit ): print('Warning, errvar/misfit cnt error', tot_cnt_misfit, tot_cnt_errvar)
    if ( tot_cnt_crps   != tot_cnt_misfit ): print('Warning, crps/misfit cnt error', tot_cnt_misfit, tot_cnt_crps)
    avg_misfit = cplot.binfldsumFIN(bin_misfit, cnt_misfit)
    avg_squerr = cplot.binfldsumFIN(bin_squerr, cnt_squerr)
    avg_errvar = cplot.binfldsumFIN(bin_errvar, cnt_errvar)
    avg_crps   = cplot.binfldsumFIN(bin_crps, cnt_crps)
    avg_tsqerr = avg_squerr + avg_errvar   
    return avg_misfit, avg_squerr, avg_errvar, avg_tsqerr, avg_crps, [grid_lon, grid_lat]

CLEVA=np.arange(-0.9, 1.1, 0.2)
CLEVF=np.arange(0, 1.1, 0.1)
cmap_full='gist_stern_r'
cmap_anom='RdYlBu_r'
def plot_binned_errors(LatLon, fields, titles, pfiles, anomis, clev_full=CLEVF, clev_anom=CLEVA):
   grid_lon, grid_lat = LatLon
   for ii in range(len(fields)):
       field=fields[ii]
       title=titles[ii]
       pfile=pfiles[ii]
       anomi=anomis[ii]
       if ( anomi == 0 ): 
           cmap=cmap_full
           levels=clev_full
       if ( anomi == 1 ): 
           cmap=cmap_anom
           levels=clev_anom
       cplot.pcolormesh(grid_lon, grid_lat, field, outfile=pfile, levels=levels, cmap=cmap, obar='horizontal')
   return
   
def plot_errors_over_range(odir, expt, date_range, obstype='DS', enn=21, clev_full=CLEVF, clev_anom=CLEVA, datadir=site5, groupby=True, bin1st=False):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    if ( len(date_range) > 1 ):
        dates=create_dates(date_range[0], date_range[1], dateinc)
        datestr0=check_date(date_range[0])
        datestr1=check_date(date_range[1])
        datestrc=datestr0+'_'+datestr1
        datestrd=datestr0+'-'+datestr1
    else:
        dates=[date_range[0]]
        datestr0=check_date(date_range[0])
        datestrc=datestr0
        datestrd=datestr0
    title1='Mean Error '+datestrd
    title2='RMSE Ensemble Mean '+datestrd
    title3='STD. Dev. Ensemble '+datestrd
    title4='RMSE Over Ensemble '+datestrd
    title5='CRPS '+datestrd
    pfile1=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.mean.png'
    pfile2=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.rmse.png'
    pfile3=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.vari.png'
    pfile4=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.rmst.png'
    pfile5=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.crps.png'
   
    titles=[title1, title2, title3, title4, title5]
    pfiles=[pfile1, pfile2, pfile3, pfile4, pfile5]

    if ( not bin1st ):
        avg_misfit, avg_squerr, avg_errvar, avg_tsqerr, avg_crps, [grid_lon, grid_lat] = bin_errors_over_range(expt, dates, obstype=obstype, enslist=enslist, datadir=datadir, groupby=groupby)
    else:
        avg_misfit, avg_squerr, avg_errvar, avg_tsqerr, avg_crps, [grid_lon, grid_lat] = bin_errors_over_erange(expt, dates, obstype=obstype, enslist=enslist, datadir=datadir) 
    fields=[avg_misfit, avg_squerr, avg_errvar, avg_tsqerr, avg_crps]
	
    outfile=odir+'/'+expt+'_'+obstype+'_'+datestrc+'.errors.nc'
    if ( obstype == 'DS' ):
        rc = write_nc_grid.write_nc_grid(fields, ['SSTerr', 'SSTsqe', 'SSTvar', 'SSTsqt', 'SSTcrps'], outfile)
    elif ( obstype == 'IS' ):
        rc = write_nc_grid.write_nc_grid(fields, ['SLAerr', 'SLAsqe', 'SLAvar', 'SLAsqt', 'SLAcrps'], outfile)
    else:
        rc = write_nc_grid.write_nc_grid(fields, ['FLDerr', 'FLDsqe', 'FLDvar', 'FLDsqt', 'FLDcrps'], outfile)


    fields=[avg_misfit, np.sqrt(avg_squerr), np.sqrt(avg_errvar), np.sqrt(avg_errvar+avg_squerr), avg_crps]
    plot_binned_errors([grid_lon, grid_lat], fields, titles, pfiles, [1, 0, 0, 0, 0], clev_full=clev_full, clev_anom=clev_anom)
    
    return [avg_misfit, avg_squerr, avg_errvar, avg_tsqerr, avg_crps] , [grid_lon, grid_lat]

def plot_scatter(odir, expt, date, axis_range=[2, 2], obs_err=0.3, obstype='DS', enslist=ens_list, datadir=site5, groupby=True):
    xmax=axis_range[0]
    ymax=axis_range[1]
    amax=np.max([xmax, ymax])
    date=check_date(date, outtype=datetime.datetime)
    datestr=check_date(date, outtype=str)
    pfile=odir+'/'+expt+'_'+obstype+'_'+datestr+'.scat'
    if ( obstype == 'DS' ):
        DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir)
    if ( obstype == 'IS' ):
        DF_list = read_IS_ensemble(expt, date, enslist=enslist, datadir=datadir)
    if ( groupby ):
        DF_mean = ensemble_vari_misfit_type(DF_list, obstype=obstype)
    else:
        DF_mean =  ensemble_vari_misfit(DF_list)
    
    misfit = DF_mean['misfit'].values
    errstd = np.sqrt(DF_mean['errvar'].values)  
    
    lat = DF_mean['Lat'].values
    alat = np.absolute(lat)
    nobs=len(misfit)
    colors=[]
    for ii in range(nobs):
        if   ( alat[ii] < 15 ): colors.append('m')
        elif ( alat[ii] < 30 ): colors.append('r')
        elif ( alat[ii] < 45 ): colors.append('y')
        elif ( alat[ii] < 60 ): colors.append('g')
        elif ( alat[ii] < 75 ): colors.append('c')
        elif ( alat[ii] < 90 ): colors.append('b')
    fig, axe = plt.subplots()
    axe.scatter(misfit, errstd, color=colors,s=0.1)
    axe.plot([0,     amax], [0, amax], color='k')
    axe.plot([0,-1.0*amax], [0, amax], color='k')
    axe.set_xlim([-1.0*xmax, xmax])
    axe.set_ylim([0, ymax])
    axe.set_xlabel('mean error')
    axe.set_ylabel('std. dev.')
    circle = plt.Circle((0.0, 0.0), obs_err, color='k', fill=False)
    axe.add_patch(circle)
    fig.savefig(pfile+'.png')
    plt.close(fig)
    return pfile+'.png'

def plot_scatter_in_range(odir, expt, date_range, axis_range=[2, 2], obs_err=0.3, enn=21, datadir=site5,obstype='DS', groupby=True):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    pfilef=odir+'/'+expt+'_'+datestrc+'.scat.gif'


    pfiles=[]    
    for date in dates:
        pfile=plot_scatter(odir, expt, date, axis_range=axis_range, obs_err=obs_err, enslist=enslist, datadir=datadir,obstype=obstype, groupby=groupby)
        pfiles.append(pfile)

    command=[['convert', '-d', '50']+pfiles+['pfilef']]
    print(command)
    subprocess.call(command)
    return
