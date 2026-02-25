#from importlib import reload
import sys
import os
import traceback
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import cartopy.crs as ccrs

import multiprocessing
from functools import partial
import itertools

import cplot
import check_date
import read_DF_VP
import read_DF_IS
import ola_functions

num_cpus = len(os.sched_getaffinity(0))
ola_file='/home/saqu500/data/ppp5/maestro_archives/SynObs/CNTLV2/SAM2/20200101/DIA/2020010100_SAM.ola'

VP_SETS = {
  'ALL'  : [  0, 'VP_GEN_INSITU_GEN'],
  'AR80' : [ 22, 'VP_GEN_INSITU_PR_PF_80'],
  'AR40' : [ 22, 'VP_GEN_INSITU_PR_PR_40'],
  'ARRF' : [ 23, 'VP_GEN_INSITU_PR_PF_RF'],
  'AR20' : [ 23, 'VP_GEN_INSITU_PR_PF_RF'],
  'BS'   : [ 24, 'VP_GEN_INSITU_PR_BA'],
  'CT'   : [ 25, 'VP_GEN_INSITU_PR_CT'],
  'GL'   : [ 26, 'VP_GEN_INSITU_PR_GL'],
  'ML'   : [ 27, 'VP_GEN_INSITU_PR_ML'],
  'TE'   : [ 28, 'VP_GEN_INSITU_PR_TE'],
  'XB'   : [ 29, 'VP_GEN_INSITU_PR_XB'],
  'XX'   : [ 30, 'VP_GEN_INSITU_PR_XX'],
  'SM'   : [ 31, 'VP_GEN_INSITU_PR_SM'],
  'PR'   : [ 32, 'VP_GEN_INSITU_PR_TX'],
  'DB'   : [ 33, 'VP_GEN_INSITU_TS_DB'],
  'FB'   : [ 34, 'VP_GEN_INSITU_TS_FB'],
  'MO'   : [ 35, 'VP_GEN_INSITU_TS_MO'],
  'TG'   : [ 36, 'VP_GEN_INSITU_TS_TG'],
  'TS'   : [ 37, 'VP_GEN_INSITU_TS_TS'],
  'OT'   : [ [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37], 'OTHER']
         }



#VP = read_DF_VP.VP_dataframe(ola_file, subset=0)
    
def ini_scatter(project='PlateCarree'):
    fig = plt.figure()
    projections, pcarree = cplot.make_projections()
    axe = plt.subplot(projection=projections[project])
    axe.set_global()
    axe.coastlines()
    return fig, axe

    
def add_scatter(fig, axe, df, color='k', label='ALL', s=4, lonname='lon', latname='lat'):  
    lon = df[lonname].values  
    lat = df[latname].values
    scat = axe.scatter(x=lon.flatten(), y=lat.flatten(), c=color, s=s, alpha=0.5, transform=ccrs.PlateCarree(), marker='s',label=label)
    return scat


def fin_scatter(fig, axe, title='TITLE', output='scatter.png'):
   axe.legend()
   axe.set_title(title)
   fig.savefig(output, bbox_inches='tight')
   plt.close(fig)
   return
   
     
def make_dataframes(file=ola_file):
    VP_DAT = {}
    for VPid in VP_SETS.keys():
        setid=VP_SETS[VPid][0]
        VP_DAT[VPid] = read_DF_VP.VP_dataframe(file, subset=setid)
    return VP_DAT

date_ref=datetime.datetime(1950,1,1,0,0)
def subset_df_by_date(df, date=datetime.date(2019, 12, 31)):
    if ( isinstance(df, dict) ):
        new_df = {}
        for i_df in df.keys():
            new_df[i_df] = subset_df_by_date(df[i_df], date=date) 
        return new_df
    if ( df.empty ): return df
    ddate = [ date_ref + datetime.timedelta(days=days) for days in df["date"]]
    idate = [ ( adate.date() == date ) for adate in ddate]
    new_df = df[idate]
    return new_df

def subset_is_by_date(df_IS, date=datetime.date(2019, 12, 31)):    
    ddate = [pd.to_datetime(df_IS['obsdate'][ii].isoformat()) for ii in df_IS.index]
    idate = [ ( adate.date() == date ) for adate in ddate]
    new_df = df_IS[idate]
    return new_df

def subset_df_by_exist(df, var='voT'):
    if ( isinstance(df, dict) ):
        new_df = {}
        for i_df in df.keys():
            new_df[i_df] = subset_df_by_exist(df[i_df], var=var) 
        return new_df
    if ( df.empty ): return df
    df_new = df[np.isfinite(df[var].values)]
    return df_new

def subset_df_by_depth(df, depth=500, var='depth_T'):
    if ( isinstance(df, dict) ):
        new_df = {}
        for i_df in df.keys():
            new_df[i_df] = subset_df_by_depth(df[i_df], depth=depth, var=var) 
        return new_df
    if ( df.empty ): return df
    df_tmp = df[np.isfinite(df[var].values)]
    df_new = df_tmp[ df_tmp[var] > depth ]
    return df_new

date=datetime.date(2020, 1, 1)
def scatter_obs_for_day(date, pdir='OBSS/'):
    date=check_date.check_date(date, outtype=datetime.date)
    days_anal = 7 - ((date.weekday() - 2)%7)
    date_anal = date + datetime.timedelta(days=days_anal)
    date_astr = date_anal.strftime("%Y%m%d")
    date_dstr = date.strftime("%Y%m%d")

    DDIR='/home/saqu500/data/ppp5/maestro_archives/SynObs/'
    EXPT='CNTLV2'
    ola_file=DDIR+EXPT+'/SAM2/'+date_astr+'/DIA/'+date_astr+'00_SAM.ola'
    print(ola_file)

    VP_DAT = make_dataframes(file=ola_file)
    VP_DAY = subset_df_by_date(VP_DAT, date=date )
    VP_TEM = subset_df_by_exist(VP_DAY, var='voT')

    for iV, V in enumerate(['T', 'S', 'T', 'S']):
        VP_VAR = subset_df_by_exist(VP_DAY, var='vo'+V)
        if ( iV > 1 ):  VP_VAR = subset_df_by_depth(VP_VAR, depth=500, var='depth_'+V)
        fig, axe = ini_scatter()
        scat1=add_scatter(fig, axe, VP_VAR['AR80'], color='b', label='ARGO ASSIM')
        scat2=add_scatter(fig, axe, VP_VAR['ARRF'], color='r', label='ARGO REF')
        scat3=add_scatter(fig, axe, VP_VAR['MO'], color='g', label='MOORINGS')
        scat4=add_scatter(fig, axe, VP_VAR['OT'], color='orange', label='OTHER TS')
        outfile=pdir+'/'+V+'observations_'+date_dstr+'.png'
        title=V+' Observations for '+date_dstr
        if ( iV > 1 ): 
            outfile=pdir+'/'+V+'observations500m_'+date_dstr+'.png'
            title=V+' Observations for '+date_dstr+' > 500m'
        fin_scatter(fig, axe, title=title, output=outfile)
    return

def scatter_SLA_for_day(date, pdir='OBSS/'):
    date=check_date.check_date(date, outtype=datetime.date)
    days_anal = 7 - ((date.weekday() - 2)%7)
    date_anal = date + datetime.timedelta(days=days_anal)
    date_astr = date_anal.strftime("%Y%m%d")
    date_dstr = date.strftime("%Y%m%d")

    DDIR='/home/saqu500/data/ppp5/maestro_archives/SynObs/'
    EXPT='CNTLV2'
    ola_file=DDIR+EXPT+'/SAM2/'+date_astr+'/DIA/'+date_astr+'00_SAM.ola'
    print(ola_file)

    IS_DAT = read_DF_IS.SSH_dataframe(ola_file)
    IS_DAY = subset_is_by_date(IS_DAT, date=date )
    isets = read_DF_IS.find_IS_isets(IS_DAY)
    print('isets', isets)

    colors=['b','r', 'g', 'orange', 'cyan', 'magenta']
    fig, axe = ini_scatter()
    labels = [str(iset) for iset in isets]
    for iis, iset in enumerate(isets):
        if ( int(iset) == 11 ): labels[iis] = 'c2'
        if ( int(iset) == 13 ): labels[iis] = 'al'
        if ( int(iset) == 15 ): labels[iis] = 'j3'
        if ( int(iset) == 17 ): labels[iis] = 's3a'
        if ( int(iset) == 18 ): labels[iis] = 's3b'
    for iis, iset in enumerate(isets):
        scat=add_scatter(fig, axe, ola_functions.subset_SSH_dataframe(IS_DAY, iset), color=colors[iis%6], label=labels[iis], lonname='Lon', latname='Lat', s=1)
    outfile=pdir+'/'+'SLA'+'observations_'+date_dstr+'.png'
    title='SLA'+' Observations for 7 days preceding '+date_dstr
    fin_scatter(fig, axe, title=title, output=outfile)
    return

def scatter_obs_for_year(year, pdir='OBSS/'):
    date=datetime.date(year,10,1)
    while date < datetime.date(year+1,1,1) :
        scatter_obs_for_day(date, pdir=pdir)
        date = date + datetime.timedelta(days=1)
    return

def scatter_obs_for_range_mp(start, final, pdir='OBSS/'):
    start_date=check_date.check_date(start, outtype=datetime.date)
    final_date=check_date.check_date(final, outtype=datetime.date)
    dates=[]
    date=start_date
    while date <= final_date :
        #scatter_obs_for_day(date, pdir=pdir)\
        dates.append(date)
        date = date + datetime.timedelta(days=1)
    nproc=np.min([num_cpus, len(dates)])
    loop_pool = multiprocessing.Pool(nproc)
    izip = list(zip(dates))
    None_list = loop_pool.starmap(partial(scatter_obs_for_day, pdir=pdir), izip)
    loop_pool.close()
    loop_pool.join()
    
    return
