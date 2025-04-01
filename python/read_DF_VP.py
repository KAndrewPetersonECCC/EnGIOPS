#from importlib import reload
import sys
import os
import traceback
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import datetime
import numpy as np
import pickle
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import subprocess

import ola_functions
import rank_histogram
import cplot
import write_nc_grid
import check_date
import inside_polygon
import nearest
import linestyles

import multiprocessing
#import multiprocessing.pool
import itertools
from functools import partial
#from concurrent.futures import ThreadPoolExecutor
#from concurrent.futures import as_completed

sys.path.insert(0, '/home/dpe000/python/properscoring-0.1')
import properscoring as ps

num_cpus = len(os.sched_getaffinity(0))
#num_cpus = os.cpu_count()

test_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'
m5dir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
m6dir='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

intconvfac=10000.0

cmap_anom = 'seismic'
cmap_zero = 'RdYlBu_r'
cmap_posd = 'gist_stern_r'

Tvars = ['voT','vfT','misfitT','sqrerrT', 'ensvarT', 'ensvvoT', 'ensvvfT', 'crpsT', 'depth_T']
Svars = ['voS','vfS','misfitS','sqrerrS', 'ensvarS', 'ensvvoS', 'ensvvfS', 'crpsS', 'depth_S']


def get_mdir(n, user='dpe000', rpn='rpnenv', grp='mrd'):
    site='site'+str(n)
    mdir='/fs/'+site+'/eccc/'+grp+'/'+rpn+'/'+user+'/maestro_archives'
    return mdir
    
def VP_dataframe(input_file, subset=0):
    df_VP = ola_functions.VP_dataframe(input_file)
    if ( subset == 0 ):
        pass
    elif ( isinstance(subset, list) ):
        df_list = []
        for iset in subset:
            df_sub = ola_functions.subset_df(df_VP, 'setID', iset)
            df_list.append(df_sub)
        df_VP = pd.concat(df_list).reset_index()
    else:
        df_VP = ola_functions.subset_df(df_VP, 'setID', subset)
    return df_VP

lls = ['lon', 'lat']
def average_duplicate_profiles(df_VP):
    """
    Average duplicate profiles in dataframe.
    Required so ensemble members only have set of distinct profiles.
    """
    df_work = df_VP.copy()
    if ( 'depth_T' in df_VP.keys() ):
        df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T'] = (intconvfac * df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T']).astype(int)
        df_TP = df_work.groupby(['lat', 'lon', 'depth_T', 'date'], as_index='False')[['lon', 'lat', 'depth_T', 'date', 'voT', 'vfT', 'misfitT']]
        df_TP_nodupl = df_TP.mean()
        df_TP_nodupl.reset_index(drop=True, inplace=True)
        #CHECK
        df_TP = df_NU.groupby(['lat', 'lon', 'depth_T', 'date'], as_index='False')[['lon', 'lat', 'depth_T', 'date', 'voT', 'vfT', 'misfitT']]
        COUNT = df_TP.count()
        DUPT = COUNT[COUNT['misfitT'] > 1]
        if ( len(DUPT) != 0 ):
            print('STILL T DUPLICATES', DUPT)
        df_TP_nodupl.loc[:, 'depth_T'] = df_TP_nodupl.loc[:, 'depth_T'] / intconvfac
    else:
        df_TP_nodupl = init_df()
    
    if ( 'depth_S' in df_VP.keys() ):
        df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S'] = (intconvfac * df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S']).astype(int)
        df_SP =  df_work.groupby(['lat', 'lon', 'depth_S', 'date'], as_index='False')[['lon', 'lat', 'depth_S', 'date', 'voS', 'vfS', 'misfitS']]
        df_SP_nodupl = df_SP.mean()
        df_SP_nodupl.reset_index(drop=True, inplace=True)
        #CHECK
        df_SP = df_NU.groupby(['lat', 'lon', 'depth_S', 'date'], as_index='False')[['lon', 'lat', 'depth_S', 'date', 'voS', 'vfS', 'misfitS']]
        COUNS = df_SP.count()
        DUPS = COUNS[COUNS['misfitS'] > 1]
        if ( len(DUPS) != 0 ):
            print('STILL S DUPLICATES', DUPS)
        df_SP_nodupl.loc[:, 'depth_S'] = df_SP_nodupl.loc[:, 'depth_S'] / intconvfac
    else:
        df_SP_nodupl = init_df()
    
    df_NU = pd.concat([df_TP_nodupl, df_SP_nodupl])

    return df_NU

def read_member_VP(expt, date, iens,  ddir=get_mdir(5),  check_duplicate=True, subset=0 ):  
    datestr8  = check_date.check_date(date, dtlen=8)
    datestr10 = check_date.check_date(date, dtlen=10)
    estr=str(iens)
    input_file=ddir+'/'+expt+estr+'/SAM2/'+datestr8+'/DIA/'+datestr10+'_SAM.ola'
    df_VP = VP_dataframe(input_file, subset=subset)
    if ( check_duplicate ):
        df_NU = average_duplicate_profiles(df_VP)
    else:
        df_NU = df_VP.copy()
    df_NU['member'] = iens
    return df_NU 

def read_ensemble_VP(expt, date, ddir=get_mdir(5), ens=list(range(21)), check_duplicate=True, mp_read=True, subset=0):
    nens = len(ens)
    df_list = []
    if ( not mp_read ):  
        df_list = []
        for ie in ens:
            df_IE = read_member_VP(expt, date, ie, ddir=ddir, check_duplicate=check_duplicate, subset=subset)
            df_list.append(df_IE)
    else:
        nproc=min([num_cpus, nens])
        read_pool = multiprocessing.Pool(nproc)
        #read_pool = multiprocessing.pool.ThreadPool()
        izip= list(zip(itertools.repeat(expt), itertools.repeat(date), ens))
        df_list = read_pool.starmap(partial(read_member_VP, ddir=ddir, check_duplicate=check_duplicate), izip)
        #result_list = read_pool.starmap_async(partial(read_member_VP, ddir=ddir, check_duplicate=check_duplicate), izip)
        read_pool.close()
        read_pool.join()
        #for df_ie in result_list.get():
        #   df_list.append(df_ie)
    df_EnVP = pd.concat(df_list).reset_index()
    return df_EnVP    

def read_deterministic_VP(expt, date, ddir=get_mdir(5), check_duplicate=True, subset=0 ):      
    datestr8  = check_date.check_date(date, dtlen=8)
    datestr10 = check_date.check_date(date, dtlen=10)
    input_file= ddir+'/'+expt+'/SAM2/'+datestr8+'/DIA/'+datestr10+'_SAM.ola'
    df_list = [ VP_dataframe(input_file, subset=subset) ]
    df_EnVP = pd.concat(df_list)
    return df_EnVP    
 
def ensemble_average_VP(df_EnVP, count=21):
    df_work = df_EnVP.copy()
    if ( 'depth_T' in df_EnVP.keys() ):
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T'].values).astype(int)
        df_TP = df_work.groupby(['lat', 'lon', 'depth_T', 'date'], as_index='False')[['voT', 'vfT', 'misfitT']]
        df_TCNT = df_TP.count()
        LT = len(df_TCNT[df_TCNT['misfitT'] < count ])     
        print('Number of SubEnsembles = ', LT)    
        NT = len(df_TCNT[df_TCNT['misfitT'] > count ])
        if ( ( NT > 0 ) ):
            print("WARNING:  Too many Ensemble Members")
            print(NT)
        df_aTP = df_TP.mean().reset_index()
        df_sTP = df_TP.var(ddof=0).reset_index()
        df_aTP[['ensvarT','ensvvoT','ensvvfT']] = df_sTP[['misfitT', 'voT', 'vfT']].values   
        df_aTP.loc[:, 'depth_T'] = df_aTP['depth_T'].values / intconvfac  
    else:
        df_aTP = init_df()
    if ( 'depth_S' in df_EnVP.keys() ):
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S'].values).astype(int)
        df_SP = df_work.groupby(['lat', 'lon', 'depth_S', 'date'], as_index='False')[['voS', 'vfS', 'misfitS']]
        df_SCNT = df_SP.count()
        LS = len(df_SCNT[df_SCNT['misfitS'] < count ])     
        print('Number of SubEnsembles = ', LS)   
        NS = len(df_SCNT[df_SCNT['misfitS'] > count ])
        if ( ( NS > 0 ) ):
            print("WARNING:  Too many Ensemble Members")
            print(NS)
        df_aSP = df_SP.mean().reset_index()
        df_sSP = df_SP.var(ddof=0).reset_index()
        df_aSP[['ensvarS','ensvvoS','ensvvfS']] = df_sSP[['misfitS', 'voS', 'vfS']].values
        df_aSP.loc[:, 'depth_S'] = df_aSP['depth_S'].values / intconvfac  
    else:
        df_aSP = init_df()
            
    df_EaVP = pd.concat([df_aTP, df_aSP])

    return df_EaVP

def add_squared_error(df_VP):
    df_NU = df_VP.copy() 
    if ( 'misfitT' in df_VP.keys() ):
        misfitT = df_VP['misfitT'].values
        sqrerrT = np.square(misfitT)
        df_NU['sqrerrT'] = sqrerrT
    if ( 'misfitS' in df_VP.keys() ):
        misfitS = df_VP['misfitS'].values
        sqrerrS = np.square(misfitS)
        df_NU['sqrerrS'] = sqrerrS
    return df_NU

def add_crps_VP(df_EaVP, df_EnVP):
    df_crps = calc_crps_VP(df_EnVP)
    if ( 'crpsT' in df_crps.keys() ): 
        print('T KEYS', df_EnVP.keys(), df_crps.keys())
        df_NUT = df_EaVP[['lon', 'lat', 'date']+[ x for x in Tvars if x !='crpsT' ]]
        df_NUT = pd.concat([df_NUT, df_crps['crpsT']], axis=1)
    else:
        df_NUT = init_df()
    if ( 'crpsS' in df_crps.keys() ): 
        print('S KEYS', df_EaVP.keys(), df_crps.keys())
        df_NUS = df_EaVP[['lon', 'lat', 'date']+[ x for x in Svars if x !='crpsS' ]]
        df_NUS = pd.concat([df_NUS, df_crps['crpsS']], axis=1)
    else:
        df_NUS = init_df()
    print("LENGTH NUX", len(df_NUT), len(df_NUS))
    df_NU = pd.concat([df_NUT, df_NUS])
    print("LENGTH NU", len(df_NU))
    return df_NU
        
def calc_crps_VP(df_EnVP):
    df_work = df_EnVP.copy()

    if ( 'depth_T' in df_EnVP.keys() ):
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T']).astype(int)
        df_TP = df_work.groupby(['lat', 'lon', 'depth_T', 'date'], as_index='False')[['misfitT']]
        CRPS_T = df_TP.apply(lambda x: calc_crps(x.values.flatten(),0)).rename('crpsT').reset_index()
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        CRPS_T.loc[:, 'depth_T'] = CRPS_T['depth_T'] / intconvfac
    else:
        CRPS_T = init_df()
    if ( 'depth_S' in df_EnVP.keys() ):
        df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S']).astype(int)
        df_SP = df_work.groupby(['lat', 'lon', 'depth_S', 'date'], as_index='False')[['misfitS']]
        CRPS_S = df_SP.apply(lambda x: calc_crps(x.values.flatten(),0)).rename('crpsS').reset_index()
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        CRPS_S.loc[:, 'depth_S'] = CRPS_S['depth_S'] / intconvfac
    else:
        CRPS_S = init_df()

    print("LENGTH CRPS", len(CRPS_T), len(CRPS_S))
    df_crps = pd.concat([CRPS_T, CRPS_S])
    return df_crps

    
def calc_crps_VPf(df_EnVP):
    df_work = df_EnVP.copy()

    if ( 'depth_T' in df_EnVP.keys() ):
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_T']), 'depth_T']).astype(int)
        df_TFO = df_work.groupby(['lat', 'lon', 'depth_T', 'date'], as_index='False')[['vfT', 'voT']]
        CRPS_T = df_TFO.apply(lambda x: calc_crps(x.vfT, x.voT.mean())).rename('crpsT').reset_index()
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        CRPS_T['depth_T'] = CRPS_T['depth_T'] / intconvfac
    else:
        CRPS_T = init_df()
    if ( 'depth_S' in df_EnVP.keys() ):
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S'] = (intconvfac*df_work.loc[np.isfinite(df_work['depth_S']), 'depth_S']).astype(int)
        df_SFO = df_work.groupby(['lat', 'lon', 'depth_S', 'date'], as_index='False')[['vfS', 'voS']]
        CRPS_S = df_SFO.apply(lambda x: calc_crps(x.vfS, x.voS.mean())).rename('crpsS').reset_index()
        # make depth_T and depth_S integers: So groupby doesn't depend on matching floats!
        CRPS_S['depth_S'] = CRPS_S['depth_S'] / intconvfac
    else:
        CRPS_S = init_df()

    df_crps = pd.concat([CRPS_T, CRPS_S])
    return df_crps

def calc_crps(ens, obs):
    if ( isinstance(ens, np.ndarray) ):
        ens=ens.flatten()
    crps = ps.crps_ensemble(obs, ens)
    return(crps)

def average_over_depth(df_EaVP):
    if ( isinstance( df_EaVP, list ) ): # then assume already isolated into T/S dataframes
        df_T = df_EaVP[0]
        df_S = df_EaVP[1]
    else:
        if ( 'depth_T' in df_EaVP.keys() ):
            df_T = df_EaVP.loc[:,Tvars]
        else:
            df_T = init_df()
        if ( 'depth_T' in df_EaVP.keys() ):
            df_S = df_EaVP.loc[:,Svars]
        else:
            df_S = init_df()


    if ( 'depth_T' in df_T.keys() ):
        df_T.loc[np.isfinite(df_T.loc[:,'depth_T']), 'depth_T'] = (intconvfac*df_T.loc[np.isfinite(df_T.loc[:,'depth_T']), 'depth_T']).astype(int)
        gl_sumT = df_T.groupby(['depth_T']).sum()
        if ( not 'countT' in df_T.keys() ):
            gl_cntT = df_T.groupby(['depth_T']).count()
            gl_supT = pd.concat([gl_sumT, gl_cntT['misfitT'].rename('countT')],axis=1)
        else:
            gl_supT = gl_sumT
        gl_supT = gl_supT.reset_index()
        gl_supT.loc[:, 'depth_T'] = gl_supT['depth_T'] / intconvfac
    else:
        gl_supT = init_series()

    if ( 'depth_S' in df_S.keys() ):
        df_S.loc[np.isfinite(df_S.loc[:,'depth_S']), 'depth_S'] = (intconvfac*df_S.loc[np.isfinite(df_S.loc[:,'depth_S']), 'depth_S']).astype(int)
        gl_sumS = df_S.groupby(['depth_S']).sum()
        if ( not 'countS' in df_S.keys() ):
            gl_cntS = df_S.groupby(['depth_S']).count()
            gl_supS = pd.concat([gl_sumS, gl_cntS['misfitS'].rename('countS')],axis=1)
        else:
            gl_supS = gl_sumS
        gl_supS = gl_supS.reset_index()
        gl_supS.loc[:, 'depth_S'] = gl_supS['depth_S'] / intconvfac
    else:
        gl_supS = init_series()

    gl_series = [gl_supT.reset_index(), gl_supS.reset_index()]
    for gl_sup in gl_series:
        for coord in ['lon', 'lat', 'lon_bin', 'lat_bin']:
            if ( coord in gl_sup.keys() ): gl_sup.drop(coord, axis=1, inplace=True)

    return gl_series
    
def calc_errors_date(date, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5), mp_read=True, subset=0):
    #mp_read = not mp   #  Need to find out how to run a child mp process inside another mp process.
    if ( deterministic ):
        df_EnVP = read_deterministic_VP(expt, date, ddir=ddir, subset=subset )
    else:
        df_EnVP = read_ensemble_VP(expt, date, ddir=ddir, ens=ens, mp_read=mp_read, subset=subset)
    df_EaVP = ensemble_average_VP(df_EnVP)
    df_EaVP = add_squared_error(df_EaVP)
    df_EaVP = add_crps_VP(df_EaVP, df_EnVP)
    
    gl_series=average_over_depth(df_EaVP)
    rgs_series = calc_region_errors(df_EaVP)
    bin_series = sum_ongrid(df_EaVP)

    return gl_series, rgs_series, bin_series
    
AREAS = { 
          'NINO34' : [ -170, -120,  -5,   5 ],
          'NINO12' : [  -90,  -80,  -10,   0 ],
          'NTrPac' : [  160,  -100,   8,  20 ],
          'STrPac' : [  160,   -90, -20,  -8 ],
          'SPacGyre' : [-179,  -90, -45, -20 ],
          'CalCurnt' : [-125, -100,  20,  40 ],
          'NPacDrft' : [ 160, -120,  45,  65 ],
          'Tropics' : [ -180,  180, -20,  20 ],
          'North40' : [ -180,  180,  40,  90 ],
          'South40' : [ -180,  180, -90, -40 ],
          'North60' : [ -180,  180,  60,  90 ],
          'NordAtl' : [ - 90,   15,  30,  65 ],
          'Pirata' : [  -40,  -30, -2.5, 2.5 ],
          'GMexico': [  -89,  -85,   24,  28 ],
          'FLStrt' : [  -81,  -75,   24,  28 ],
          'GlfSt1' : [  -70,  -62,   36,  40 ],
          'GlfSt2' : [  -62,  -45,   38,  42 ],
          'NFIS'   : [  -48,  -37,   45,  55 ],
          'ACC'    : [ -180,  180,  -90, -45 ]
        }
        
def make_poly_from_box( box ):
    X0 = box[0]
    X1 = box[1]
    Y0 = box[2]
    Y1 = box[3]
    polygon = [ [X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1], [X0, Y0] ]
    return polygon

# Defined
# /home/dpe000/data/ppp5/ORDS/GITHUB/giops/GIOPS_RIOPS_sam2_coolskin/src/ROA_ITF/mod_domain.F90
# /home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_regions    
PAREAS = { 'NINO34' : make_poly_from_box( AREAS['NINO34'] ),
           'NINO12' : make_poly_from_box( AREAS['NINO12'] ),
           'SPacGyre' : make_poly_from_box( AREAS['SPacGyre']),
           'CalCurnt' : make_poly_from_box( AREAS['CalCurnt']),
           'Tropics' : make_poly_from_box( AREAS['Tropics'] ),
           'NordAtl' : make_poly_from_box( AREAS['NordAtl'] ),
           'Pirata'  :  make_poly_from_box( AREAS['Pirata'] ),
           'GlfSt1'  : make_poly_from_box( AREAS['GlfSt1'] ),
           'GlfSt2'  : make_poly_from_box( AREAS['GlfSt2'] ),
           'NFIS'    : make_poly_from_box( AREAS['NFIS'] ),
           'NPacGyre' : [[130.,20.], [160.,45.], [240.,45.], [240.,20.], [130.0, 20.0]],
           'ISBsn'    : [[-35.,55.],[-25.,62.],[-10.,62.],[-10.,55],[-35.,55.]],
           'ACC'      : make_poly_from_box( AREAS['ACC'] ),
           'North60'  : make_poly_from_box( AREAS['North60'] ),
         }
         
   
def calc_region_errors(df_EaVP):
    regions = PAREAS.keys()
    rgs_series = []
    for region in regions:
        polygon = PAREAS[region]
        points_are_inside = inside_polygon.test_inside_xyarray(polygon, df_EaVP.lon.values, df_EaVP.lat.values)[0]
        df_region = df_EaVP[points_are_inside]
        rg_series = average_over_depth(df_region)
        rgs_series.append(rg_series)
    return rgs_series

DELTA=2.0
def put_ongrid(df, delta=DELTA):
    df_g = df.copy()
    bins_lons, bins_lats, xlon, xlat, query_lon, query_lat = nearest.grid(delta=delta)
    df_g['lat_bin'] = nearest.nearest3(query_lat, bins_lats, df['lat'].values)
    df_g['lon_bin'] = nearest.nearest3(query_lon, bins_lons, df['lon'].values)
    df_g.drop(['lat', 'lon'],axis=1)
    return df_g

ll_bin = ['lon_bin', 'lat_bin']     
def sum_ongrid(df_EaVP, delta=DELTA):
    df_g = put_ongrid(df_EaVP, delta=delta)   
    ## NOT CORRECDT -- ADD depth_T/depth_S to sum/cnt!!!!

    df_g.loc[np.isfinite(df_g['depth_T']), 'depth_T'] = (intconvfac*df_g.loc[np.isfinite(df_g['depth_T']), 'depth_T']).astype(int)    
    df_g.loc[np.isfinite(df_g['depth_S']), 'depth_S'] = (intconvfac*df_g.loc[np.isfinite(df_g['depth_S']), 'depth_S']).astype(int)    
    
    df_sumT = df_g[Tvars+ll_bin].groupby(['lon_bin', 'lat_bin', 'depth_T']).sum().reset_index()
    df_cntT = df_g[Tvars+ll_bin].groupby(['lon_bin', 'lat_bin', 'depth_T']).count().reset_index()
    df_supT = pd.concat([df_sumT, df_cntT['misfitT'].rename('countT')],axis=1)
    df_sumS = df_g[Svars+ll_bin].groupby(['lon_bin', 'lat_bin', 'depth_S']).sum().reset_index()
    df_cntS = df_g[Svars+ll_bin].groupby(['lon_bin', 'lat_bin', 'depth_S']).count().reset_index()
    df_supS = pd.concat([df_sumS, df_cntS['misfitS'].rename('countS')],axis=1)
    
    df_supT.loc[:, 'depth_T'] = df_supT['depth_T'] / intconvfac
    df_supS.loc[:, 'depth_S'] = df_supS['depth_S'] / intconvfac

    return [df_supT, df_supS]

def init_df():
    df_nan = pd.DataFrame(np.nan, index=[], columns=[])
    return df_nan

def init_series():
    df_nan = init_df().sum()
    return df_nan

def init_dataframes():
    gl_supT = init_df()
    gl_supS = init_df()
    gl_series = [gl_supT, gl_supS]
    
    rgs_series = []
    for region in  PAREAS.keys():
        rg_supT = init_df()
        rg_supS = init_df()
        rgs_series.append([rg_supT, rg_supS])
    
    df_supT = init_df()
    df_supS = init_df()
    bin_series = [df_supT, df_supS]
    
    return gl_series, rgs_series, bin_series

def addto_frames(old_df, add_df, listin=False):

    if ( listin ):
        new_list = []
        for ilist, df in enumerate(old_df):
            new_dfs = addto_frames(df, add_df[ilist], listin=False)
            new_list.append(new_df)
        return new_list

    rgs_T, rgs_S = old_df
    add_T, add_S = add_df
    
    new_T = pd.concat([rgs_T, add_T]).reset_index()
    new_S = pd.concat([rgs_T, add_S]).reset_index()
    return (new_T, new_S)
    
def addto_sums( old_sums, add_sums):
    gl_series, rgs_series, bin_series = old_sums
    add_gl_series, add_rgs_series, add_bin_series = add_sums
    
    gl_sumT, gl_sumS = gl_series
    gl_addT, gl_addS = add_gl_series
    
    gl_T = pd.concat([gl_sumT, gl_addT])
    gl_S = pd.concat([gl_sumS, gl_addS])
    
    gl_T.loc[np.isfinite(gl_T['depth_T']), 'depth_T'] = (intconvfac*gl_T.loc[np.isfinite(gl_T['depth_T']), 'depth_T']).astype(int)
    gl_S.loc[np.isfinite(gl_S['depth_S']), 'depth_S'] = (intconvfac*gl_S.loc[np.isfinite(gl_S['depth_S']), 'depth_S']).astype(int)
        
    gl_newT = gl_T.groupby('depth_T').sum().reset_index()
    gl_newS = gl_S.groupby('depth_S').sum().reset_index()
    
    gl_newT.loc[:, 'depth_T'] = gl_newT['depth_T'] / intconvfac
    gl_newS.loc[:, 'depth_S'] = gl_newS['depth_S'] / intconvfac
    
    #print(gl_newT['countT'], gl_newS['countS'])
    new_gl_series = [gl_newT, gl_newS]
    
    new_rgs_series = []
    for ir, rg_series in enumerate(rgs_series):
        add_rg_series = add_rgs_series[ir]
        rg_sumT, rg_sumS = rg_series
        rg_addT, rg_addS = add_rg_series
        
        rg_T = pd.concat([rg_sumT, rg_addT])
        rg_S = pd.concat([rg_sumS, rg_addS])

        rg_T.loc[np.isfinite(rg_T['depth_T']), 'depth_T'] = (intconvfac*rg_T.loc[np.isfinite(rg_T['depth_T']), 'depth_T']).astype(int)
        rg_S.loc[np.isfinite(rg_S['depth_S']), 'depth_S'] = (intconvfac*rg_S.loc[np.isfinite(rg_S['depth_S']), 'depth_S']).astype(int)

        rg_newT = rg_T.groupby('depth_T').sum().reset_index()
        rg_newS = rg_S.groupby('depth_S').sum().reset_index()

        rg_newT.loc[:, 'depth_T'] = rg_newT['depth_T'] / intconvfac
        rg_newS.loc[:, 'depth_S'] = rg_newS['depth_S'] / intconvfac

        new_rgs_series.append([rg_newT, rg_newS])
        
    gr_sumT, gr_sumS = bin_series
    gr_addT, gr_addS = add_bin_series
    
    gr_T = pd.concat([gr_sumT, gr_addT])
    gr_S = pd.concat([gr_sumS, gr_addS])
    
    gr_T.loc[np.isfinite(gr_T['depth_T']), 'depth_T'] = (intconvfac*gr_T.loc[np.isfinite(gr_T['depth_T']), 'depth_T']).astype(int)
    gr_S.loc[np.isfinite(gr_S['depth_S']), 'depth_S'] = (intconvfac*gr_S.loc[np.isfinite(gr_S['depth_S']), 'depth_S']).astype(int)

    gr_newT = gr_T.groupby(['lat_bin', 'lon_bin', 'depth_T']).sum().reset_index()
    gr_newS = gr_S.groupby(['lat_bin', 'lon_bin', 'depth_S']).sum().reset_index()

    gr_newT.loc[:, 'depth_T'] = gr_newT['depth_T'] / intconvfac
    gr_newS.loc[:, 'depth_S'] = gr_newS['depth_S'] / intconvfac

    #print(gr_newT['countT'], gr_newS['countS'])
    new_bin_series = [gr_newT, gr_newS]
        
    return new_gl_series, new_rgs_series, new_bin_series     

def init_vertical_array(nt, nd, nT, nS):
    narea = len(PAREAS.keys())
    grgs_binv = []
    for iarea in range(narea+1):   # includes global
        grgs_binv.append( (np.NaN * np.ones((nt, nd, nT)), np.NaN * np.ones((nt, nd, nS))) )
    return grgs_binv

def addto_vertical_array(idate, grgs_binv, grgs_series, depth, TTvars, SSvars):
    nseries = len(grgs_binv)
    nt, nd, nT = grgs_binv[0][0].shape
    nt, nd, nS = grgs_binv[0][1].shape
    for iseries in range(nseries):
        dfT, dfS = grgs_series[iseries][:]
        for ik in range(nd):
            dfLT = dfT[dfT['depth_T'] == depth[ik]]
            if ( len(dfLT) != 0 ):
                for ikey, key in enumerate(TTvars):
                    grgs_binv[iseries][0][idate, ik, ikey] = dfLT[key].values
            dfLS = dfS[dfS['depth_S'] == depth[ik]]
            if ( len(dfLS) != 0 ):
                for ikey, key in enumerate(SSvars):
                    grgs_binv[iseries][1][idate, ik, ikey] = dfLS[key].values
    return grgs_binv        
        
def cycle_thru_dates(dates, expt, ens=list(range(21)), deterministic=False, ddir=get_mdir(5),  mp_date=False, mp_read=True, subset=0):
    gl_series, rgs_series, bin_series = init_dataframes()
    depth = np.loadtxt('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_depths')
    TTvars = Tvars.copy()
    TTvars[Tvars.index('depth_T')] = 'countT'
    SSvars = Svars.copy()
    SSvars[Svars.index('depth_S')] = 'countS'
 
    nd=len(depth)
    nt=len(dates)
    nT=len(TTvars)
    nS=len(SSvars)
    
    grgs_binv = init_vertical_array(nt, nd, nT, nS)
    ADD_RESULTS=[]
    if (mp_date):
        nproc=min([num_cpus, len(dates)])
        process_pool = multiprocessing.Pool(nproc)
        izip = list(zip(dates, itertools.repeat(expt)))
        #print(izip)
        RTN_LIST = process_pool.starmap_async(partial(calc_errors_date, ens=ens, deterministic=deterministic, ddir=ddir, mp_read=False, subset=subset), izip)
        process_pool.close()
        process_pool.join()
        ADD_RESULTS = RTN_LIST.get()
    else:     
       for idate,date in enumerate(dates):
           ADD_RESULTS.append(calc_errors_date(date, expt, ens=ens, deterministic=deterministic, ddir=ddir, mp_read=mp_read, subset=subset))
    for idate, date in enumerate(dates):
       add_gl_series, add_rgs_series, add_bin_series = ADD_RESULTS[idate]
       #add_gl_series, add_rgs_series, add_bin_series = calc_errors_date(date, expt, ens=ens, deterministic=deterministic, ddir=ddir, mp_read=mp_read, subset=subset)   
       gl_series, rgs_series, bin_series = addto_sums( ( gl_series, rgs_series, bin_series ), (add_gl_series, add_rgs_series, add_bin_series) )
       day_gl_series, day_rgs_series = apply_averaging(add_gl_series, add_rgs_series)
       grgs_binv = addto_vertical_array(idate, grgs_binv, [day_gl_series]+day_rgs_series, depth, TTvars, SSvars)

    # Apply Final Averaging on area averages
    gl_series_avg, rgs_series_avg = apply_averaging(gl_series, rgs_series)
    
    # Subset bin_series to Levels
    Bin_Levels = loop_levels(bin_series)
    Bin_Levels_Avg = apply_depth_averaging(Bin_Levels) 
    return gl_series_avg, rgs_series_avg, Bin_Levels_Avg, grgs_binv

def final_mean( df_sum, count_name, coord_list ):
   df_avg = df_sum.copy()
   keys = df_avg.keys()
   keys = keys.drop(coord_list)
   
   for key in keys:
       if ( key != count_name ):
           df_avg[key] = df_sum[key].values / df_sum[count_name].values

   return df_avg   

def final_mean_list( list_sums ):
    list_avgs = []
    for df_sum in list_sums:
        if ( isinstance(df_sum, list ) ): 
            df_avg = final_mean_list( df_sum)
        else:
            count_name='count'
            if ( 'countT' in df_sum.keys() ): count_name='countT' 
            if ( 'countS' in df_sum.keys() ): count_name='countS'
            coord_list = []
            for coord in ['depth', 'depth_T', 'depth_S', 'lat', 'lon', 'bin_lat', 'bin_lon']:
                if ( coord in df_sum.keys() ): coord_list.append(coord)
            df_avg = final_mean(df_sum, count_name, coord_list)
        list_avgs.append(df_avg)
    return list_avgs

def put_bin_onlevels(bin_series, depth_range, llvars=['lon_bin', 'lat_bin'], dvars=['depth_T', 'depth_S'] ):
    depthmin=depth_range[0]
    depthmax=depth_range[1]
    dTvar=dvars[0]
    dSvar=dvars[1]
    if ( isinstance(bin_series, list) ): # assume already separated into S/T   
        df_binT, df_binS = bin_series
    else:
        allTvars = Tvars+llvars
        allSvars = Svars+llvars
        if ( 'countT' in bin_series.keys() ): allTvars+['countT']
        if ( 'countS' in bin_series.keys() ): allSvars+['countS']
        df_binT = bin_series[ allTvars ]
        df_binS = bin_series[ allSvars ]
    
    belowminT = df_binT[dTvar] > depthmin 
    belowminS = df_binS[dSvar] > depthmin
    if ( depthmax == -1 ):
        abovemaxT = pd.Series(True, index=df_binT.index)
        abovemaxS = pd.Series(True, index=df_binS.index)
    else:
        abovemaxT = df_binT[dTvar] <= depthmax 
        abovemaxS = df_binS[dSvar] <= depthmax

    df_levelT = df_binT[belowminT & abovemaxT]
    df_levelS = df_binS[belowminS * abovemaxS]
    return df_levelT, df_levelS

Levels = [  [0, 200.0], [0, 500.0], [200.0, 500.0], [500.0, 2000.0], [0, 50.0], [0, 10.0], [0, 5.0]]

def loop_levels(df_bin_list, these_levels=Levels, llvars=['lon_bin', 'lat_bin'], dvars=['depth_T', 'depth_S'] ):
    Bin_Levels = []
    for levels in these_levels:
        bin_Levels = put_bin_onlevels( df_bin_list, levels, llvars=llvars, dvars=dvars )
        Bin_Levels.append(bin_Levels)
    return Bin_Levels
    
def apply_depth_averaging(bin_Levels, llvars=['lon_bin', 'lat_bin']):
    if ( ( isinstance(bin_Levels[0], list) ) or ( isinstance(bin_Levels[0], tuple) ) ): 
        bin_Levels_avg = []
        for bin_levels in bin_Levels:
            bin_Levels_avg.append(apply_depth_averaging(bin_levels, llvars=llvars))
    else:
        binT=bin_Levels[0]
        binS=bin_Levels[1]
        newbinT = binT.copy()
        newbinS = binS.copy()
        newbinT['depth_T'] = binT['depth_T'].values * binT['countT'].values
        newbinS['depth_S'] = binS['depth_S'].values * binS['countS'].values
        dfT = newbinT.groupby(llvars).sum().reset_index()
        dfS = newbinS.groupby(llvars).sum().reset_index()
        dfT = final_mean(dfT, 'countT', llvars )
        dfS = final_mean(dfS, 'countS', llvars )
        bin_Levels_avg = (dfT, dfS)
        
    return bin_Levels_avg
        

def apply_averaging(gl_series, rgs_series):

    depth_name = ['depth_T', 'depth_S']
    count_name=['countT', 'countS']

    ald_series = rgs_series+[gl_series]
    ald_series_avg = []
    for sng_series in ald_series:
        sng_series_avg = []
        for iF, sumF in enumerate(sng_series):
            avg = final_mean(sumF, count_name[iF], [depth_name[iF]])
            sng_series_avg.append(avg)
        ald_series_avg.append(sng_series_avg)
    rgs_series_avg = ald_series_avg[0:len(rgs_series)]
    gl_series_avg = ald_series_avg[-1]

    return gl_series_avg, rgs_series_avg
    
linestyle_str, linestyle_tup = linestyles.return_linestyles()
    
def plot_profiles(df_profiles, outpre='PLOTS/'):
    for ifld, fld in enumerate(['T','S']):
        plot_profile(df_profiles[ifld], fld, outpre=outpre)
    return
        
def profile(df_profile, fld='T', maxdepth=200, outpre='PLOTS/'):
    flabel = 'Temperature (\N{degree sign}C)'
    if ( fld=='S'): flabel = 'Salinity (PSU)'
    dvar = 'depth_'+fld
    depth = df_profile[dvar].values
    
    fig1, axe1 = plt.subplots()
    
    merr = df_profile['misfit'+fld].values
    rmse = df_profile['sqrerr'+fld].values
    crps = df_profile['crps'+fld].values
    estd = df_profile['ensvar'+fld].values
    stde = np.sqrt(rmse - np.square(merr) ) 
    rmse = np.sqrt(rmse)
    estd = np.sqrt(estd)
    
    axe1.semilogy( merr, depth, linestyle='--', color='k', label='mean')
    axe1.semilogy( rmse, depth, linestyle='-', color='k', label='rmse')
    axe1.semilogy( estd, depth, linestyle=':', color='k', label='sprd')
    axe1.semilogy( crps, depth, linestyle='-.', color='k', label='crps')
    axe1.semilogy( stde, depth, linestyle=linestyle_tup['-..-..'], color='k', label='stde')
    axe1.invert_yaxis()
    axe1.legend()
    axe1.set_xlabel(flabel)
    axe1.set_ylabel('depth (m)')
    fig1.savefig(outpre+fld+'profile.png')
    plt.close(fig1)
    
    fig2, axe2 = plt.subplots()
    axe2.plot( merr, depth, linestyle='--', color='k', label='mean')
    axe2.plot( rmse, depth, linestyle='-', color='k', label='rmse')
    axe2.plot( estd, depth, linestyle=':', color='k', label='sprd')
    axe2.plot( crps, depth, linestyle='-.', color='k', label='crps')
    axe2.plot( stde, depth, linestyle=linestyle_tup['-..-..'], color='k', label='stde')
    axe2.set_ylim([0, maxdepth])
    axe2.invert_yaxis()
    axe2.legend()
    axe2.set_xlabel(flabel)
    axe2.set_ylabel('depth (m)')
    mstr=str(maxdepth)
    fig2.savefig(outpre+fld+'profile_'+mstr+'m.png')
    plt.close(fig2)

    return

def plot_profiles_multi(df_profile_list, labels, title='', outpre='PLOTS/Ex', maxdepths=[200, 500, 2000], noensstat=False, nostdstat=False):
    for ifld, fld in enumerate(['T','S']):
        plot_profile_multi([df_profiles[ifld] for df_profiles in df_profile_list], labels, fld, outpre=outpre, maxdepths=maxdepths, noensstat=noensstat, nostdstat=nostdstat)
    return
    
def plot_profiles_norm_multi(df_profile_list, labels, title='', outpre='PLOTS/Ex', maxdepths=[200, 500, 2000], noensstat=False, nostdstat=False):
    for ifld, fld in enumerate(['T','S']):
        plot_profile_norm_multi([df_profiles[ifld] for df_profiles in df_profile_list], labels, fld, outpre=outpre, maxdepths=maxdepths, noensstat=noensstat, nostdstat=nostdstat)
    return
    
def plot_profile_multi(df_profile_list, labels, fld='T', maxdepths=[200, 2000], outpre='PLOTS/Ex', noensstat=False, nostdstat=False):
    flabel = 'Temperature (\N{degree sign}C)'
    if ( fld=='S'): flabel = 'Salinity (PSU)'
    nexpts = len(df_profile_list)
    title = fld+'-profile'
    dvar = 'depth_'+fld
    if ( ( not isinstance(maxdepths, list) ) and ( not isinstance(maxdepths, tuple) ) ): maxdepths=[maxdepths]
    
    figL, axeL = plt.subplots()
    axeL.axvline(x=0, color='k', linestyle='-')
    figD=[]; axeD=[]
    for maxdepth in maxdepths:
        fig, axe = plt.subplots()
        axe.axvline(x=0, color='k', linestyle='-')
        figD.append(fig); axeD.append(axe)

    colors = ['r', 'b', 'g', 'c', 'm']    

    line_elementsL = []
    line_elementsD = []
    expt_elementsL = []
    expt_elementsD = []
    lines = [ 'mean', 'rmse', 'sprd', 'crps', 'stde' ]
    linel = [ '--', '-', ':', '-.', linestyle_tup['-..-..'] ]
    these_lines = lines.copy()
    if ( noensstat ):
        these_lines = [ 'mean', 'rmse', 'stde' ]
    if ( nostdstat ):
        these_lines.remove('stde')    

    nlines = len(these_lines)
    for lina in these_lines:
        iline = lines.index(lina)
        linestyle = linel[iline]
        line_elementsL.append( Line2D([0], [0], color='k', ls=linestyle, label=lina) )
        line_elementsd = []
        for iplot, maxdepth in enumerate(maxdepths):
           line_elementsd.append( Line2D([0], [0], color='k', ls=linestyle, label=lina) )
        line_elementsD.append(line_elementsd)

    nlinee = []
    for ip, df_profile in enumerate(df_profile_list):
        lwidth=1
        if ( ip == 0 ): lwidth=3
        label = labels[ip]
        color = colors[ip%5]
        depth = df_profile[dvar].values
        merr = df_profile['misfit'+fld].values
        rmse = df_profile['sqrerr'+fld].values
        crps = df_profile['crps'+fld].values
        evar = df_profile['ensvar'+fld].values
        estd = df_profile['ensvar'+fld].values
        stde = np.sqrt(rmse - np.square(merr) ) 

        rmse = np.sqrt(rmse)
        estd = np.sqrt(estd)
        errors = [ merr, rmse, estd, crps, stde] 
        these_lines = lines
        nlinee.append(len(these_lines))
        print('Max EVAR', np.max(evar))
        these_lines = lines.copy()
        if ( np.all(evar==0) ):
            these_lines = [ 'mean', 'rmse', 'stde' ] 
            print('evar == 0', label, outpre) 
        if ( noensstat ):
            these_lines = [ 'mean', 'rmse', 'stde' ]
        if ( nostdstat ):
            these_lines.remove('stde')
        for lina in these_lines:
            iline=lines.index(lina)
            linestyle = linel[iline]
            if ( iline == 1 ):
                ll, = axeL.semilogy( errors[iline], depth, linestyle=linestyle, linewidth=lwidth, color=color, label=label)
                expt_elementsL.append(ll)
                expt_elementsd=[]
                for iplot, maxdepth in enumerate(maxdepths):
                    lt, = axeD[iplot].plot( errors[iline], depth, linewidth=lwidth, linestyle=linestyle, color=color, label=label)
                    expt_elementsd.append(lt)
                expt_elementsD.append(expt_elementsd)
            else:
                ll, = axeL.semilogy( errors[iline], depth, linestyle=linestyle, color=color)
                for iplot, maxdepth in enumerate(maxdepths):
                    lt, = axeD[iplot].plot( errors[iline], depth, linewidth=lwidth, linestyle=linestyle, color=color)

    expt_legendL = axeL.legend(handles=expt_elementsL, loc='upper right')
    line_legendL = axeL.legend(handles=line_elementsL, loc='lower right')
    axeL.set_title(title)
    axeL.add_artist(expt_legendL)
    axeL.add_artist(line_legendL)
    axeL.invert_yaxis()
    axeL.set_xlabel(flabel)
    axeL.set_ylabel('depth (m)')
    figL.savefig(outpre+fld+'profile.png')
    figL.savefig(outpre+fld+'profile.pdf')
    plt.close(figL)

    for iplot, maxdepth in enumerate(maxdepths):
        mstr=str(maxdepth)
        expt_elements = [ expt_elementsD[iexpt][iplot] for iexpt in range(nexpts) ]
        line_elements = [ line_elementsD[iline][iplot] for iline in range(nlines) ]
        if ( maxdepth > 200 ):
            locexpt='center right'
            locline='lower right'
        else:
            locexpt='center'
            locline='lower center'
            
        expt_legendD = axeD[iplot].legend(handles=expt_elements, loc=locexpt)
        line_legendD = axeD[iplot].legend(handles=line_elements, loc=locline)
        axeD[iplot].set_title(title)
        axeD[iplot].add_artist(expt_legendD)
        axeD[iplot].add_artist(line_legendD)
        axeD[iplot].set_ylim([0, maxdepth])
        axeD[iplot].invert_yaxis()
        axeD[iplot].set_xlabel(flabel)
        axeD[iplot].set_ylabel('depth (m)')
        figD[iplot].savefig(outpre+fld+'profile_'+mstr+'m.png')
        figD[iplot].savefig(outpre+fld+'profile_'+mstr+'m.pdf')
        plt.close(figD[iplot])

    return

    
def plot_profile_norm_multi(df_profile_list, labels, fld='T', maxdepths=[200, 2000], outpre='PLOTS/Ex', noensstat=False, nostdstat=False):
    flabel = 'Temperature (\N{degree sign}C)'
    if ( fld=='S'): flabel = 'Salinity (PSU)'
    nexpts = len(df_profile_list) - 1
    title = fld+'-profile'
    dvar = 'depth_'+fld
    if ( ( not isinstance(maxdepths, list) ) and ( not isinstance(maxdepths, tuple) ) ): maxdepths=[maxdepths]
    
    colors = ['b', 'g', 'c', 'm', 'r']    

    expt_elementsL = []
    expt_elementsD = []
    lines = [ 'rmse', 'sprd', 'crps', 'stde' ]
    these_lines = lines.copy()
    if ( noensstat ):
        these_lines = [ 'mean', 'rmse', 'stde' ]
    if ( nostdstat ):
        these_lines.remove('stde')    

    nlines = len(these_lines)
    figA = []; axeA=[]
    for this_plot in these_lines:
        figL, axeL = plt.subplots()
        axeL.axvline(x=0, color='k', linestyle='-')
        figD=[]; axeD=[]
        for maxdepth in maxdepths:
            fig, axe = plt.subplots()
            axe.axvline(x=0, color='k', linestyle='-')
            figD.append(fig); axeD.append(axe)
        figA.append([figL]+figD), axeA.append([axeL]+axeD)

    expt_elementsA=[]
    for ip, df_profile in enumerate(df_profile_list[1:]):
        lwidth=1
        label = labels[ip]
        color = colors[(ip-1)%5]
        depth = df_profile[dvar].values
        merr = df_profile['misfit'+fld].values
        rmse = df_profile['sqrerr'+fld].values
        crps = df_profile['crps'+fld].values
        evar = df_profile['ensvar'+fld].values
        estd = df_profile['ensvar'+fld].values
        stde = np.sqrt(rmse - np.square(merr) ) 
        rmse = np.sqrt(rmse)
        estd = np.sqrt(estd)
        if ( ip == 0 ):
          ref_errors = [ rmse, estd, crps, stde] 
          ref_rmse = rmse
          ref_estd = estd
          ref_crps = crps
          ref_stde = stde 
        else:
          errors = [rmse/ref_rmse, estd/ref_estd, crps/ref_crps, stde/ref_stde]
        these_lines = lines
        if ( ip > 0 ):
            for lina in these_lines:
                iline=lines.index(lina)
                iiline=these_lines.index(lina)
                print('DEBUG', iiline, iline, len(axeA))
                axeL = axeA[iiline][0]
                figL = figA[iiline][0]
                axeD = axeA[iiline][1:]
                figD = figA[iiline][1:]
                ll, = axeL.semilogy( errors[iline], depth, linestyle='-', linewidth=1, color=color, label=label)
                expt_elementsL.append(ll)
                expt_elementsd=[]
                for iplot, maxdepth in enumerate(maxdepths):
                    lt, = axeD[iplot].plot( errors[iline], depth, linewidth=1, linestyle='-', color=color, label=label)
                    expt_elementsd.append(lt)
                expt_elementsD.append(expt_elementsd)
            expt_elementsA.append([expt_elementsL]+expt_elementsD)

    for lina in these_lines:
        expt_elementsL = expt_elementsA[lina][0]
        expt_elementsD = expt_elementsA[lina][1:]
        expt_legendL = axeL.legend(handles=expt_elementsL, loc='upper right')
        #line_legendL = axeL.legend(handles=line_elementsL, loc='lower right')
        axeL.set_title(title)
        axeL.add_artist(expt_legendL)
        #axeL.add_artist(line_legendL)
        axeL.invert_yaxis()
        axeL.set_xlabel(flabel)
        axeL.set_ylabel('depth (m)')
        figL.savefig(outpre+fld+'profile_'+lina+'.png')
        figL.savefig(outpre+fld+'profile_'+lina+'.pdf')
        plt.close(figL)

        for iplot, maxdepth in enumerate(maxdepths):
            mstr=str(maxdepth)
            expt_elements = [ expt_elementsD[iexpt][iplot] for iexpt in range(nexpts) ]
            #line_elements = [ line_elementsD[iline][iplot] for iline in range(nlines) ]
            if ( maxdepth > 200 ):
                locexpt='center right'
                locline='lower right'
            else:
                locexpt='center'
                locline='lower center'
            
            expt_legendD = axeD[iplot].legend(handles=expt_elements, loc=locexpt)
            #line_legendD = axeD[iplot].legend(handles=line_elements, loc=locline)
            axeD[iplot].set_title(title)
            axeD[iplot].add_artist(expt_legendD)
            #axeD[iplot].add_artist(line_legendD)
            axeD[iplot].set_ylim([0, maxdepth])
            axeD[iplot].invert_yaxis()
            axeD[iplot].set_xlabel(flabel)
            axeD[iplot].set_ylabel('depth (m)')
            figD[iplot].savefig(outpre+fld+'profile_'+lina+'_'+mstr+'m.png')
            figD[iplot].savefig(outpre+fld+'profile_'+lina+'_'+mstr+'m.pdf')
            plt.close(figD[iplot])

    return

def plot_df_field(binF, drop=['ensvvo', 'ensvvf'], outpre='PLOTS/', titpre=''):
   if ( isinstance(binF, list) or isinstance(binF, tuple) ): 
       for ibinF in binF:
           plot_df_field(ibinF, drop=drop, outpre=outpre)
       return
   binP = binF.copy()
   lon_bin = binF['lon_bin'].values
   lat_bin = binF['lat_bin'].values
   if ( 'depth_T' in binP.keys() ): binP.drop(['depth_T'], axis=1, inplace=True)
   if ( 'depth_S' in binP.keys() ): binP.drop(['depth_S'], axis=1, inplace=True)
   binP.drop(['lon_bin', 'lat_bin'], inplace=True, axis=1)
   for idrop in drop:
       if ( idrop+'T' in binP.keys() ): binP.drop([idrop+'T'], axis=1, inplace=True)
       if ( idrop+'S' in binP.keys() ): binP.drop([idrop+'S'], axis=1, inplace=True)

   print('Full Field', outpre, list(binP.keys()))   
   for vari in binP.keys():
       fld = binF[vari].values
       varn = vari
       LEVS = None
       if ( vari[0:6] == 'sqrerr' ):
           fld=np.sqrt(fld)
           varn='rmse'+vari[6]
           cmap = cmap_posd
           LEVS = np.arange(0.0,1.1,0.1)
       if ( vari[0:6] == 'ensvar' ):
           fld = np.sqrt(fld)
           varn='estd'+vari[6]
           cmap = cmap_posd
           LEVS = np.arange(0.0,1.1,0.1)
       if ( vari[0:6] == 'misfit' ):
           varn='merr'+vari[6]
           LEVS=np.arange(-0.9,0.9,0.2)
           cmap=cmap_anom
       if ( vari[0:5] == 'count' ):
            cmap=cmap_posd
       if ( ( vari[0:2] == 'vo' ) or ( vari[0:2] == 'vf' ) ):
           varn=vari
           if ( vari[2] == 'T' ):
               LEVS = np.arange(-5, 40.0, 5.0)
           else:
               LEVS = np.arange(30.0, 41.0, 1.0)
           LEVS = None
           cmap = cmap_posd
       outfile=outpre+varn+'.png'
       #print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn
       print(varn, 'Max/Min', np.max(fld), np.min(fld)) 
       cplot.bin_pcolormesh(lon_bin, lat_bin, fld, title=title, levels=LEVS, ddeg=DELTA, outfile=outfile, obar='horizontal')
   return


def plot_diff_field(bin1, bin2, drop=['ensvvo', 'ensvvf', 'vf', 'vo'], titpre='', outpre='PLOTS/'):
   if ( isinstance(bin1, list) or isinstance(bin1,tuple) ): 
       for ibin, ibin1 in enumerate(bin1):
           iibin1=bin1[ibin]
           iibin2=bin2[ibin]
           plot_diff_field(iibin1, iibin2, drop=drop, outpre=outpre)
       return
   binP1 = bin1.copy()
   binP2 = bin2.copy()
   if ( 'depth_T' in binP1.keys() ): binP1.drop(['depth_T'], axis=1, inplace=True)
   if ( 'depth_S' in binP1.keys() ): binP1.drop(['depth_S'], axis=1, inplace=True)
   if ( 'depth_T' in binP2.keys() ): binP2.drop(['depth_T'], axis=1, inplace=True)
   if ( 'depth_S' in binP2.keys() ): binP2.drop(['depth_S'], axis=1, inplace=True)
   for idrop in drop:
       if ( idrop+'T' in binP1.keys() ): binP1.drop([idrop+'T'], axis=1, inplace=True)
       if ( idrop+'S' in binP1.keys() ): binP1.drop([idrop+'S'], axis=1, inplace=True)
       if ( idrop+'T' in binP2.keys() ): binP2.drop([idrop+'T'], axis=1, inplace=True)
       if ( idrop+'S' in binP2.keys() ): binP2.drop([idrop+'S'], axis=1, inplace=True)

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
           varn='rmse'+vari[6]
       if ( vari[0:6] == 'ensvar' ):
           varn='estd'+vari[6]
       cmap = cmap_anom
       LEVS = np.arange(-0.9, 1.1, 0.2)
       if ( vari[0:5] == 'count' ):
            LEVS = None
       #print('TITLE', titpre, len(titpre))
       if ( len(titpre) > 0 ):
           title=titpre+' '+varn
       else:
           title=varn+' difference'
       outfile=outpre+varn+'.png'
       cplot.bin_pcolormesh(lon_bin, lat_bin, fldd_values, title=title, levels=LEVS, ddeg=DELTA, outfile=outfile, obar='horizontal', cmap=cmap)
   return

def process_expt(dates, expt, ens_passed, this_ddir, mp_read=True, mp_date=False, subset=0):
    deterministic = False
    #print(ens_passed)
    if ( ( isinstance(ens_passed, list) ) or ( isinstance(ens_passed, np.ndarray) ) ): ens = ens_passed
    if ( isinstance(ens_passed, type(None) ) ): deterministic = True
    if ( isinstance(ens_passed, int) ):
         if ( ens_passed == 0 ): 
             deterministic = True
             ens=0
         else:
             ens=list(range(ens_passed))
                
    gl_series, rgs_series, bin_series, grgs_varray = cycle_thru_dates(dates, expt, ens=ens, deterministic=deterministic, ddir=this_ddir, mp_read=mp_read, mp_date=mp_date, subset=subset)
    return  expt, gl_series, rgs_series, bin_series, grgs_varray
     
def cycle_thru_expts(dates, expts, enss, ddir=get_mdir(5), mp_expt=False, mp_read=True, mp_date=False, subset=0):

    print( "MP SETTINGS", mp_expt, mp_read )
    if ( mp_expt and mp_read ):
        print('WARNING:  Multitasking within multitasking not working')
        mp_read = not mp_expt

    gl_list = []
    rgs_list = []
    bin_list = []
    grgs_list = []
    expt_list = []
    if ( isinstance(ddir, list) ): 
        ddirs=ddir
    else:
        ddirs = [ ddir for expt in expts ]

    if ( not mp_expt ):
        for iexpt, expt in enumerate(expts):
            ens_passed = enss[iexpt]
            dir_passed = ddirs[iexpt]
            expt_rtn, gl_series, rgs_series, bin_series, grgs_varray = process_expt(dates, expt, ens_passed, dir_passed, mp_read=mp_read, mp_date=mp_date, subset=subset)
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            grgs_list.append(grgs_varray)
            expt_list.append(expt_rtn)
    else:
        nproc=min([num_cpus, len(expts)])
        process_pool = multiprocessing.Pool(nproc)
        izip = list(zip(itertools.repeat(dates), expts, enss, ddirs))
        #print(izip)
        RTN_LIST = process_pool.starmap_async(partial(process_expt, mp_read=False, mp_date=False, subset=subset), izip)
        process_pool.close()
        process_pool.join()
        FIN_LIST = RTN_LIST.get()
        sort_list = []
        for isort, fin_element in enumerate(FIN_LIST):
            expt_rtn, gl_series, rgs_series, bin_series, grgs_varray = fin_element
            if ( expt_rtn != expts[isort] ):
                print("WARNING: Experiments order not conserved!!")
                print(isort, expt_rtn, expts[isort])
            sort_list.append(expts.index(expt_rtn))
            gl_list.append(gl_series)
            rgs_list.append(rgs_series)
            bin_list.append(bin_series)
            grgs_list.append(grgs_varray)
            expt_list.append(expt_rtn)
        expt_copy = expt_list.copy()
        expt_list = [ expt_list[isort] for isort in sort_list ]
        gl_list = [ gl_list[isort] for isort in sort_list ]
        rgs_list = [ rgs_list[isort] for isort in sort_list ]
        bin_list = [ bin_list[isort] for isort in sort_list ]
        grgs_list = [ grgs_list[isort] for isort in sort_list ]
        print("SORTED ", ( list(expt_list) == list(expts) ), expt_list, expts, sort_list, expt_copy )
    return gl_list, rgs_list, bin_list, grgs_list

def produce_stats_plot( date_range, expts, enss, labels=None, outdir=None, ddir=get_mdir(5), mp_expt=False, mp_read=False, mp_date=True, outdirpre='', noensstat=False, nostdstat=False, subset=0):
    if ( mp_expt and mp_read ):
        print('WARNING:  Multitasking within multitasking not working')
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
    gl_list, rgs_list, bin_list, grgs_list = cycle_thru_expts(dates, expts, enss, ddir=ddir, mp_expt=mp_expt, mp_read=mp_read, mp_date=mp_date, subset=subset)
    print("FINISHED CYCLE THROUGH ALL EXPERIMENT DATES")
    outpreoutg=outdirpre+outdir[0] +'/'+'Profiles_'+datestrr+'_'+'Global'+'_'
    plot_profiles_multi(gl_list, labels, title='Global', outpre=outpreoutg, noensstat=noensstat, nostdstat=nostdstat)
    try:
        plot_profiles_norm_multi(gl_list, labels, title='Global', outpre=outpreoutg, noensstat=noensstat, nostdstat=nostdstat)
    except:
        print(traceback.print_exc())
        print("FAILURE of NORM PROFILES")
    for iarea, area in enumerate(PAREAS.keys()):
        reg_list = [ rgs_series[iarea] for rgs_series in rgs_list ]
        title=area
        outpreouta=outdirpre+outdir[0] +'/'+'Profiles_'+datestrr+'_'+area+'_'
        plot_profiles_multi(reg_list, labels, title=title, outpre=outpreouta, noensstat=noensstat, nostdstat=nostdstat)
        try:
            plot_profiles_norm_multi(reg_list, labels, title=title, outpre=outpreouta, noensstat=noensstat, nostdstat=nostdstat)
        except:
            print(traceback.print_exc())
            print("FAILURE of NORM PROFILES")
    print("FINISHED PROFILE PLOTS")

    try:
      for ilevel, level in enumerate(Levels):
        levstr=str(level[0])+'_'+str(level[1])
        for iexpt, expt in enumerate(expts):
            binL = bin_list[iexpt][ilevel]
            outpreoutb=outdirpre+outdir[iexpt]+'/'+'Levels_'+datestrr+'_'+levstr+'_'
            titpre=labels[iexpt]+' '+datestrr+' '+levstr
            #print('TITLE', titpre, len(titpre))
            try:
                plot_df_field(binL, titpre=titpre, outpre=outpreoutb)
                print("FINISHED FULL FIELD LEVEL : ", levstr, labels[iexpt])
            except:
                print(traceback.print_exc())
                print("FAILURE FULL FIELD LEVEL : ", levstr, labels[iexpt])
            if ( iexpt == 0 ): 
                bin0=binL
            else:
                odir=outdirpre+outdir[0]+'_'+outdir[iexpt]
                titpre=labels[0]+'-'+labels[iexpt]+' '+datestrr+' '+levstr
                #print('TITLE', titpre, len(titpre))
                outpreoutb=odir+'/'+'Levels_'+datestrr+'_'+levstr+'_'
                try:
                    plot_diff_field(bin0, binL, titpre=titpre, outpre=outpreoutb)
                    print("FINISHED DIFF FIELD LEVEL : ", levstr, labels[iexpt])
                except:
                    print(traceback.print_exc())
                    print("FAILURE DIFF FIELD LEVEL : ", levstr, labels[iexpt])
        print("FINISHED LEVEL", ilevel)
    except:
        print(traceback.print_exc())
        print("FAILURE LEVEL PLOTS")

    print("FINISHED LEVEL PLOTS")

    Tvarslist = ['countT', 'misfitT', 'sqrerrT', 'ensvarT', 'crpsT']
    Svarslist = ['countS', 'misfitS', 'sqrerrS', 'ensvarS', 'crpsS']
    narea = len(grgs_list[0])
    narea = len(PAREAS.keys())+1
    for iexpt, expt in enumerate(expts):
        for iarea in range(narea): 
            if ( iarea == 0 ): 
                areanam='Global'     
            else:
                areanam = list(PAREAS.keys())[iarea-1]     
            dfT_binv, dfS_binv = grgs_list[iexpt][iarea]
            plotdiff=True
            if ( iexpt == 0 ):
                dfT_bin0 = dfT_binv
                dfS_bin0 = dfS_binv
                exp0 = expt
                plotdiff=False
            #print(dfT_binv.shape, dfS_binv.shape)
            for iTS, binv in enumerate([dfT_binv, dfS_binv]):
                bin0 = [dfT_bin0, dfS_bin0][iTS]
                varslist = [Tvarslist, Svarslist][iTS]
                plot_hov_vars(dates, binv, bin0, iTS, labels[iexpt], labels[0], outdir[iexpt], outdir[0], areanam, plotdiff=plotdiff, outdirpre=outdirpre)
    print("FINISHED HOVMULLER PLOTS")
            

    return

def plot_hov_vars(dates, binv, bin0, ibin, lab, lab0, dir, dir0, areanam, plotdiff=True, outdirpre=''):

    depth = get_depth()

    datestr1 = check_date.check_date(dates[0], dtlen=8)
    datestr2 = check_date.check_date(dates[-1], dtlen=8)
    datestrr = datestr1 + '_' + datestr2
    
    TTvars = Tvars.copy()
    TTvars[Tvars.index('depth_T')] = 'countT'
    SSvars = Svars.copy()
    SSvars[Svars.index('depth_S')] = 'countS'

    Tvarslist = ['countT', 'misfitT', 'sqrerrT', 'ensvarT', 'crpsT']
    Svarslist = ['countS', 'misfitS', 'sqrerrS', 'ensvarS', 'crpsS']

    ## I really should have kept this a dataframe.  Convoluted!!
    Tindex = [TTvars.index(Tvar) for Tvar in Tvarslist]
    Sindex = [SSvars.index(Svar) for Svar in Svarslist]

    if ( ibin == 0 ): 
        INDEXES = Tindex
        INVARIS = Tvarslist
    if ( ibin == 1 ): 
        INDEXES = Sindex
        INVARIS = Svarslist
    
    for ii in range(len(INDEXES)):
        iindex=INDEXES[ii]
        varnam=INVARIS[ii]
        dird=dir0+'_'+dir
        outfile=outdirpre+dir+'/'+'Hovmuller_'+datestrr+'_'+areanam+'_'+varnam+'.png'
        outfild=outdirpre+dird+'/'+'Hovmuller_'+datestrr+'_'+areanam+'_'+varnam+'.png'
        pltarray = np.squeeze(binv[:, :, iindex])
        pldarray = np.squeeze(bin0[: ,: ,iindex]) - pltarray
        posd=True
        cmap_here = cmap_posd
        if ( varnam[0:6] == 'misfit' ): 
            posd=False
            cmap_here = cmap_zero
        CLEV = find_good_contour_levels(pltarray, posd=posd)
        ALEV = find_good_contour_levels(pldarray)
        if ( np.all(CLEV==0) ): CLEV=None
        if ( np.all(ALEV==0) ): ALEV=None
        #print('CLEV/ALEV', CLEV, ALEV)
        for ymax in [500, 2000]: 
            ystr=''
            if ( ymax != 2000 ): ystr=str(int(ymax))
            outfile=outdirpre+dir+'/'+'Hovmuller'+ystr+'_'+datestrr+'_'+areanam+'_'+varnam+'.png'
            outfild=outdirpre+dird+'/'+'Hovmuller'+ystr+'_'+datestrr+'_'+areanam+'_'+varnam+'.png'
            posd=True
            cmap_here = cmap_posd
            if ( varnam[0:6] == 'misfit' ): 
                posd=False
                cmap_here = cmap_zero
            if not np.all(np.isnan(pltarray)):
              plot_hovmuller(dates, depth, pltarray, outfile=outfile, ymax=ymax, cmap=cmap_here, levels=CLEV)
            if ( plotdiff ):
                if not np.all(np.isnan(pldarray)):
                    plot_hovmuller(dates, depth, pldarray, levels=ALEV, outfile=outfild, ymax=ymax, cmap=cmap_zero)
        
    return
    
def plot_hovmuller(dates, depth_local, plt_array, outfile='hovmuller.png', ymax=2000, cmap=cmap_anom, levels=None):
    #myFmt = mdates.DateFormatter('%m/%d')
    fig, axe = plt.subplots() 
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    axe.xaxis.set_major_locator(locator)
    axe.xaxis.set_major_formatter(formatter)
    if ( isinstance(levels, type(None) ) ):
        norm=None
    else:
        Ncolors=plt.get_cmap(cmap).N
        norm = clr.BoundaryNorm(levels, ncolors=Ncolors, clip=True)
    if ( isinstance(norm, type(None) ) ):
        mesh=axe.pcolormesh( dates, depth_local, np.transpose(plt_array), cmap=cmap)
    else:
        mesh=axe.pcolormesh( dates, depth_local, np.transpose(plt_array), cmap=cmap, norm=norm)
    axe.set_ylim([0, ymax])                                                    
    axe.invert_yaxis()                                         
    cbar_fig=fig.colorbar(mesh,orientation='horizontal') 
    fig.savefig(outfile)
    plt.close(fig)                                     
    return

def get_depth():
    depth = np.loadtxt('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_depths')
    return depth

def find_good_contour_levels(fld, posd=False):
    if ( not posd ):
        BASE1=np.arange(-9.0, 10.0, 2.0)/10.0
        BASE5=np.arange(-4.5,  5.0, 1.0)/10.0
        BASE2=np.arange(-1.8,  2.0, 0.4)/10.0
    else:
        BASE1=np.arange(0, 10.1, 1.0) / 10.0
        BASE5=np.arange(0,  5.1, 0.5) / 10.0
        BASE2=np.arange(0,  2.1, 0.2) / 10.0
    
    MAXV = np.nanmax(np.abs(fld))   
    MINV = np.nanmin(fld)
    LOGV = np.ceil(np.log10(MAXV))
    
    if ( MAXV / 10**LOGV <= 0.2 ): 
      #print('pick 2')
      BASE=BASE2*10**LOGV
    elif ( MAXV / 10**LOGV <= 0.5 ): 
      #print('pick 5')
      BASE=BASE5*10**LOGV
    else: 
      #print('pick 1')
      BASE= BASE1*10**LOGV     
    #print(MINV, MAXV, BASE)
    return BASE
    
    
