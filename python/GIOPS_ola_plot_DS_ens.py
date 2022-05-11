'''
Script purpose:
Read and produce graphics for DS (SST) data.
Statistics are computed over bined grid points (2x2 degrees)
Graphics are produced for mean misfit [O-P], misfit rms and mean obs data number
'''

import struct
import argparse
import os, sys, getopt
import numpy as np
from netCDF4 import Dataset
import pandas as pd
from netCDF4 import num2date
import datetime
from mpl_toolkits.basemap import Basemap
from bisect import bisect_left
import warnings
from scipy.spatial import cKDTree
import time
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import cm
from matplotlib.colors import ListedColormap
import  mimetypes
import cPickle as pickle

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import ola_functions

'''
Plot DS data from netCDF ola files
'''

warnings.filterwarnings('ignore')

start = time.time()

def nearest3(tree, myList, myNumbers):
    '''
    Group to the nearest values given in myList
    inputs:
    tree: preprocessed myNumbers date using cKDTree tool 
    myList: list used to group data
    myNumber: original data 
    '''
    x = myNumbers
    x.shape = x.shape + (1,)
    dists, inds = tree.query(x)
    return myList[inds]
    
def df_combine(df):

    '''
    Combine dataframe by bining and computing stats over lat/lon
    input: raw dataframe
    output: combined dataframe
    '''
    # Square misfit
    df['misfit_2'] = df['misfit'].values **2       # square
    df['obssq'] = df['obs'].values**2 
    df['modsq'] = df['mod'].values**2

    # Group data by 2deg x 2deg 
    df['lat_int'] = nearest3(query_lat, bins_lats, df['Lat'].values)
    df['lon_int'] = nearest3(query_lon, bins_lons, df['Lon'].values)

    # Bining and computing statistics
    avg   = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['lat_int', 'lon_int','misfit']]; avg.rename(columns={'misfit':'misfit_avg'}, inplace=True)
    count = df.groupby(['lat_int','lon_int'], as_index=False).count()[['misfit']]; count.rename(columns={'misfit':'obs_count'}, inplace=True)
    ms    = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['misfit_2']]; ms.rename(columns={'misfit_2':'ms'}, inplace=True)
    obs   = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['obs', 'obssq']]; 
    mod   = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['mod', 'modsq']]; 
    ms['rms'] = np.sqrt(ms['ms'].values)
    df_grd = pd.concat([avg, count, ms, obs, mod], axis=1)
    return df_grd

def combine_ensemble(df):
    '''
    Combine dataframe by bining and computing stats over lat/lon
    input: raw dataframe
    output: combined dataframe
    '''
    if len(df) > 0:
        df_cmd = df.groupby(['lat_int','lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
	enmn_bias           = ola_functions.weighted_average(df, 'misfit_avg', 'obs_count', ['lat_int','lon_int'])
	enmn_sqme           = enmn_bias**2
	enmn_sqee           = ola_functions.weighted_average(df, 'ms', 'obs_count', ['lat_int','lon_int'])
        df_cmd['enmn_bias'] = enmn_bias
	df_cmd['enmn_sqme'] = enmn_sqme
	df_cmd['enmn_sqee'] = enmn_sqee
	df_cmd['enmn_evar'] = enmn_sqee - enmn_sqme
        df_cmd['enmn_rms']  = ola_functions.weighted_average(df, 'rms', 'obs_count', ['lat_int','lon_int'])
	enmn_obs            = ola_functions.weighted_average(df, 'obs', 'obs_count', ['lat_int','lon_int'])
	enmn_osq            = ola_functions.weighted_average(df, 'obssq', 'obs_count', ['lat_int','lon_int'])
	enmn_obs            = ola_functions.weighted_average(df, 'obs', 'obs_count', ['lat_int','lon_int'])
	enmn_osq            = ola_functions.weighted_average(df, 'obssq', 'obs_count', ['lat_int','lon_int'])
        df_cmd['enmn_obs']  = enmn_obs
	df_cmd['enmn_ovar'] = enmn_osq - enmn_obs**2
	enmn_obs            = ola_functions.weighted_average(df, 'obs', 'obs_count', ['lat_int','lon_int'])
	enmn_osq            = ola_functions.weighted_average(df, 'obssq', 'obs_count', ['lat_int','lon_int'])
	enmn_mod            = ola_functions.weighted_average(df, 'mod', 'obs_count', ['lat_int','lon_int'])
	enmn_msq            = ola_functions.weighted_average(df, 'modsq', 'obs_count', ['lat_int','lon_int'])
	df_cmd['enmn_mod']  = enmn_mod
	df_cmd['enmn_mvar'] = enmn_msq - enmn_mod**2
	
    else:
        df_cmd = pd.DataFrame(np.nan, index=[], columns=[])
    return df_cmd

def combine_raw_ensemble(df):
    
    df_copy = df.copy()
    df_copy['misfit_2'] = np.square(df_copy['misfit'].values)
    df_ensm = df_copy.groupby(['Lat','Lon'], as_index=False).mean()[['Lat', 'Lon', 'tt', 'obs', 'mod', 'misfit', 'misfit_2']];
    df_ensm['ensvar'] = df_ensm['misfit_2'].values - np.square(df_ensm['misfit'].values)

    # Square misfit
    df_ensm['sqrerr'] = df_ensm['misfit'].values **2       # square

    # Group data by 2deg x 2deg 
    df_ensm['lat_int'] = nearest3(query_lat, bins_lats, df_ensm['Lat'].values)
    df_ensm['lon_int'] = nearest3(query_lon, bins_lons, df_ensm['Lon'].values)

    # Bining and computing statistics
    avg   = df_ensm.groupby(['lat_int','lon_int'], as_index=False).mean()[['lat_int', 'lon_int','misfit','ensvar','sqrerr']]
    count = df_ensm.groupby(['lat_int','lon_int'], as_index=False).count()[['misfit']]; count.rename(columns={'misfit':'obs_count'}, inplace=True)
    df_grd = pd.concat([avg, count], axis=1)
    return df_grd
   
def combine_global(df):

    '''
    Combine dataframe by bining and computing stats over lat/lon
    input: raw dataframe
    output: combined dataframe
    '''
    if len(df) > 0:
        df_cmd = df.groupby(['lat_int','lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
        df_cmd['mean_bias'] = ola_functions.weighted_average(df, 'enmn_bias', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_sqme'] = ola_functions.weighted_average(df, 'enmn_sqme', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_evar'] = ola_functions.weighted_average(df, 'enmn_evar', 'obs_count', ['lat_int','lon_int'])
        df_cmd['mean_rms1'] = ola_functions.weighted_average(df, 'enmn_rms', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_sqee'] = ola_functions.weighted_average(df, 'enmn_sqee', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_obs']  = ola_functions.weighted_average(df, 'enmn_obs', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_ovar'] = ola_functions.weighted_average(df, 'enmn_ovar', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_mod']  = ola_functions.weighted_average(df, 'enmn_mod', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_mvar'] = ola_functions.weighted_average(df, 'enmn_mvar', 'obs_count', ['lat_int','lon_int'])
	
    else:
        df_cmd = pd.DataFrame(np.nan, index=[], columns=[])
    return df_cmd

def combine_hlobal(df):

    '''
    Combine dataframe by bining and computing stats over lat/lon
    input: raw dataframe
    output: combined dataframe
    '''
    if len(df) > 0:
        df_cmd = df.groupby(['lat_int','lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
        df_cmd['mean_bias'] = ola_functions.weighted_average(df, 'misfit', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_evar'] = ola_functions.weighted_average(df, 'ensvar', 'obs_count', ['lat_int','lon_int'])
	df_cmd['mean_sqme'] = ola_functions.weighted_average(df, 'sqrerr', 'obs_count', ['lat_int','lon_int'])
    else:
        df_cmd = pd.DataFrame(np.nan, index=[], columns=[])
    return df_cmd

def plot_SST_misfit_map(df, typ, fld='new_bias'):
    '''
    Purpose: plot SST misfit map
    Arguments:
    df: dataframe containing data
    '''
    if ( isinstance(fld, list) ):
        for sfld in fld:
	    plot_SST_misfit_map(df, typ, fld=sfld)
	return
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    df['lon_int'][df['lon_int'] < 0] += 360
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    #fig = plt.figure(figsize=(8, 8))
    if typ == 'SST':
        plt.title(suite_name + ': SST average misfit in deg', fontsize=16)
    elif typ == 'SST_NIGHT':
        plt.title(suite_name + ': SST_NIGHT average misfit in deg', fontsize=16)
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)

    norm = matplotlib.colors.Normalize(vmin = -1.0, vmax = 1.0, clip = False)
    if ( fld == 'new_bias' ): values = df['new_bias'].values
    if ( fld == 'gnu_bias' ): values = df['gnu_bias'].values
    if ( fld == 'omb_bias' ): values = df['new_obs'].values - df['new_mod'].values
    colors = plt.cm.coolwarm(norm(values))
    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
    clevs = np.linspace(-1.0, 1.0, 20)
    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
    ticks = [-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
    c.ax.tick_params(labelsize=12)
    if ( typ == 'SST' ):
        if ( fld == 'new_bias' ):
	    outfile = output_dir +'/ENS_SST_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png'
	elif ( fld == 'gnu_bias' ):
	    outfile = output_dir +'/EGS_SST_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png'
        elif ( fld == 'omb_bias' ):
	    outfile = output_dir +'/ENS_SST_' + sdate + '_' + fdate + '_AVR_MISFIT2_map.png'
    elif typ == 'SST_NIGHT':
        if ( fld == 'new_bias' ):
            outfile = output_dir +'/ENS_SST_NIGHT_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png'
	elif ( fld == 'gnu_bias' ):
	    outfile = output_dir +'/EGS_SST_NIGHT_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png'
        elif ( fld == 'omb_bias' ):
            outfile = output_dir +'/ENS_SST_NIGHT_' + sdate + '_' + fdate + '_AVR_MISFIT2_map.png'
    plt.savefig(outfile)
    return


def plot_SST_misfit_rms_map(df, typ, fld='new_rms1'):
    '''
    Purpose: plot SST misfit RMS map
    Arguments:
    df: dataframe containing data
    '''
    #new_fields  = [ 'new_bias',  'new_sqme',  'new_rms1',  
    #                 'new_sqee',  'new_obs', 
    #                 'new_ovar',  'new_mod',  'new_mvar']
    
    if ( isinstance(fld, list) ):
        for sfld in fld:
	    plot_SST_misfit_rms_map(df, typ, fld=sfld)
	return
    if ( fld == 'new_rms1' ):
        values = np.square(df['new_rms1'].values)
        descript = 'average member misfit rms (mean of sqrts)'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_RMS_ONE_map.png'
    elif ( fld == 'new_rms2' ):
        values = (df['new_sqee'].values)
        descript = 'average member misfit rms (sqrt mean of squares)'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_RMS_TWO_map.png'
	suite_name + ': ' + typ +' ' + descript + ' in deg'
    elif ( fld == 'new_rmsm' ):
        values = (df['new_sqme'].values)
        descript = 'average ensemble mean misfit rms'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_RMS_ENM_map.png'
    elif ( fld == 'gnu_rmsm' ):
        values = (df['gnu_sqme'].values)
        descript = 'average ensemble mean misfit rms'
        outfile = output_dir +'/EGS_'+typ+'_' + sdate + '_' + fdate + '_RMS_ENM_map.png'
    elif ( fld == 'new_estd' ):
        values = (df['new_evar'].values)
        descript = 'average std error'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_STD_ERR_map.png'
    elif ( fld == 'gnu_estd' ):
        values = (df['gnu_evar'].values)
        descript = 'average std error'
        outfile = output_dir +'/EGS_'+typ+'_' + sdate + '_' + fdate + '_STD_ERR_map.png'
    elif ( fld == 'new_ostd' ):
        values = (df['new_ovar'].values)
        descript = 'average std observations'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_STD_OBS_map.png'
    elif ( fld == 'new_mstd' ):
        values = (df['new_mvar'].values)
        descript = 'average std background'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_STD_BKG_map.png'
    elif ( fld == 'new_rmsc' ):
        values = ( df['new_sqee'] - df['new_evar'] )
        descript = 'calculate misfit rms'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_RMS_CAL_map.png'
    elif ( fld == 'new_rmsr' ):  ## NOTE: MIGHT BE NEGATIVE
        values = ( df['new_sqme'] - df['new_evar'] )
        descript = 'residual misfit'
        outfile = output_dir +'/ENS_'+typ+'_' + sdate + '_' + fdate + '_RMS_RES_map.png'
    elif ( fld == 'gnu_rmsr' ):  ## NOTE: MIGHT BE NEGATIVE
        values = ( df['gnu_sqme'] - df['gnu_evar'] )
        descript = 'residual misfit'
        outfile = output_dir +'/EGS_'+typ+'_' + sdate + '_' + fdate + '_RMS_RES_map.png'
    elif ( fld == 'gnu_rmst' ):  ## NOTE: MIGHT BE NEGATIVE
        values = ( df['gnu_sqme'] - df['gnu_evar'] - 0.09)
        descript = 'obs incl residual misfit'
        outfile = output_dir +'/EGS_'+typ+'_' + sdate + '_' + fdate + '_RMS_RET_map.png'
    values = np.array(values)
    print(fld, 'Max/Min -- SQUARED', np.max(values), np.min(values))
    ineg = np.where(values < 0 )
    if ( len(ineg[0]) != 0 ):
        print(fld, ": Warning Negative Values")
	try:
	   values[ineg] = 0.0
	except:
	   print( type(values) )
	   print(ineg)
    values=np.sqrt(values)
    title=suite_name + ': ' + typ +' ' + descript + ' in deg'    

    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    df['lon_int'][df['lon_int'] < 0] += 360
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    #fig = plt.figure(figsize=(8, 8))
    plt.title(title, fontsize=16)

    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    cmap = matplotlib.cm.get_cmap('jet')
    normalize = matplotlib.colors.Normalize(vmin=0., vmax=2.0)
    colors = [cmap(normalize(v)) for v in values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max', format='%.1f')
    c.ax.tick_params(labelsize=12)
    plt.savefig(outfile)
    return
   

def plot_SST_obs_count_map(df, typ, var_count='new_count'):
    '''
    Purpose: plot SST obs number map
    Arguments:
    df: dataframe containing data
    '''
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    df['lon_int'][df['lon_int'] < 0] += 360
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6))
    #fig = plt.figure(figsize=(8, 8))
    if typ == 'SST':
        plt.title(suite_name + ': SST observations number', fontsize=16)
    elif typ == 'SST_NIGHT':
        plt.title(suite_name + ': SST_NIGHT observations number', fontsize=16)
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    cmap = matplotlib.cm.get_cmap('YlOrRd')
    normalize = matplotlib.colors.Normalize(vmin=0., vmax=np.percentile(df[var_count].values, 90))
    colors = [cmap(normalize(v)) for v in df[var_count].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max')
    c.ax.tick_params(labelsize=12)
    number='NUM_DATA'
    ensem='ENS'
    if ( var_count == 'gnu_count' ): ensem='EGS'
    if typ == 'SST':
        plt.savefig(output_dir +'/'+ensem+'_SST_' + sdate + '_' + fdate + '_'+number+'_map.png')
    elif typ == 'SST_NIGHT':
        plt.savefig(output_dir +'/'+ensem+'_SST_NIGHT_' + sdate + '_' + fdate + '_'+number+'_map.png')


def transform_180(df, short=False):
    df_ = df.copy()
    df_['lon_int'][df_['lon_int'] == -180] = 180
    xx = df_.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
    if ( not short ):
        xx.rename(columns={'obs_count':'new_count'}, inplace=True)
    else:
        xx.rename(columns={'obs_count':'gnu_count'}, inplace=True)
    df_list = [xx]
    if ( not short):
        mean_fields = ['mean_bias', 'mean_sqme', 'mean_evar', 'mean_rms1', 'mean_sqee', 'mean_obs', 'mean_ovar', 'mean_mod', 'mean_mvar']
        new_fields  = [ 'new_bias',  'new_sqme',  'new_evar',  'new_rms1',  'new_sqee',  'new_obs',  'new_ovar',  'new_mod',  'new_mvar']
    else:
        mean_fields = ['mean_bias', 'mean_sqme', 'mean_evar']
        new_fields  = [ 'gnu_bias',  'gnu_sqme',  'gnu_evar']
    for ifld in range(len(mean_fields)):
        org_field = mean_fields[ifld]
	new_field = new_fields[ifld]
	yy = df_.groupby(['lat_int', 'lon_int'], as_index=False).mean()[[org_field]]
	yy.rename(columns={org_field:new_field}, inplace=True)
	df_list.append(yy)
    df_ = pd.concat(df_list, axis=1)
    return df_

family = ['IS','VP','UV','DS']

global rga_DS, iga_DS
global Ndup, jpwork_array, TM, icycle


# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",       required=True, help="Experiment name")
ap.add_argument("--input_dir",   required=True, help="Experiment path")
ap.add_argument("--output_dir",  required=True, help="Output path")
ap.add_argument("--start_date",  required=True, help="Start date")
ap.add_argument("--final_date",  required=True, help="Final date")
ap.add_argument("--stype",       required=True, help="Experiment type W(weekly) or D(daily)")
ap.add_argument("--replace", required=True, help="Replacement String for path")
ap.add_argument("--ensemble", required=True, nargs="*", type=int, help="Ensemble Members")

suite_name   = ap.parse_args().suite
input_dir    = ap.parse_args().input_dir
output_dir   = ap.parse_args().output_dir
sdate        = ap.parse_args().start_date
fdate        = ap.parse_args().final_date
exp_id       = ap.parse_args().stype
replace      = ap.parse_args().replace
ensemble     = ap.parse_args().ensemble


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not output_dir.endswith('/'):
    output_dir = output_dir + '/'


start_date = datetime.datetime.strptime(sdate, "%Y%m%d")
final_date = datetime.datetime.strptime(fdate, "%Y%m%d")


# Make sure dates are in order
if start_date > final_date:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)


# Print entered arguments
print 'Experiment name: ', suite_name
print 'Start date:      ', sdate
print 'End date:        ', fdate

# Number of dates during the cycle
num_days = (final_date - start_date).days

# List of dates of the cycle
if exp_id.upper() == 'W':
    dates = [start_date + datetime.timedelta(days = x) for x in range(0, num_days + 7, 7)]
elif exp_id.upper() == 'D':
    dates = [start_date + datetime.timedelta(days = x) for x in range(0, num_days + 1)]


# Define lats and lons for 2x2 bins
bins_lons = np.arange(-180, 181, 2)
bins_lats = np.arange(-90, 91, 2)
xlon = bins_lons ; xlon.shape = bins_lons.shape + (1,)
xlat = bins_lats ; xlat.shape = bins_lats.shape + (1,)
query_lon = cKDTree(xlon)
query_lat = cKDTree(xlat)


df_g_list_sst = []
df_g_list_sst_night = []
df_h_list_sst = []
df_h_list_sst_night = []

tmpdir = '/home/dpe000/data/eccc-ppp4/tempo/' + suite_name + '/'
os.system('mkdir -p ' + tmpdir)

for num_dates in range(len(dates)):
  dateS = datetime.datetime.strftime(dates[num_dates], "%Y%m%d")
  print 'Working on date: ', dateS
  df_e_list_sst = []
  df_e_list_sst_night = []
  df_r_list_sst = []
  df_r_list_sst_night = []
  for ie, ens in enumerate(ensemble):
    str_ens=str(ens)
    tmpdir = '/home/dpe000/data/eccc-ppp4/tempo/' + suite_name + '/' + str_ens + '/' 
    os.system('mkdir -p ' + tmpdir)
    replace0=replace+'0'
    replacen=replace+str_ens
    input_ens = input_dir.replace(replace0, replacen)
    print input_dir, input_ens, replace0, replacen

    if os.path.exists(input_ens + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz'):                # case where file is zipped
        os.system('rm -rf ' + tmpdir + '*')
        os.system('cp ' + input_ens + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz ' + tmpdir)
        os.system('gunzip ' + tmpdir + dateS + '00_SAM.ola.gz')
        input_file = tmpdir + dateS + '00_SAM.ola'
    else: # case where file is not zipped
        input_file = input_ens + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola'

    print(input_file)
    # Read DS data
    rga_DS, iga_DS = ola_functions.read_data(input_file, 'DS')

#        rga_DS = f.variables['rga_DS'][:]
#        iga_DS = f.variables['iga_DS'][:]

    # Extract variables and build dataframe

    lon = rga_DS[0, :]        # Longitude
    lat = rga_DS[1, :]        # Latitude
    tt  = rga_DS[2, :]        # Time (days since 1950-01-01 00:00:00)
    ov  = rga_DS[3, :]        # Observation value
    fv  = rga_DS[4, :]        # Model equivalent value
    av  = rga_DS[5, :]        # Analysis value (not used for now)
    dv  = rga_DS[6, :]        # Misfit value
    oe  = rga_DS[7, :]        # Observation error
    #
    duid  = iga_DS[0, :]      # Track number
    Tstp  = iga_DS[1, :]      # Model time step corresonding to observation time
    setid = iga_DS[8, :]      # Instrument indicator
    qc    = iga_DS[9, :]      # QC values (O: good obs;  1: bad obs)

    index = range(len(lon))
    df_DS        = pd.DataFrame(lon, index=index, columns=['Lon'])
    df_DS['Lat'] = pd.DataFrame(lat, index=index)
    df_DS['tt']  = pd.DataFrame(tt,  index=index)
    df_DS['obs']  = pd.DataFrame(ov,  index=index)
    df_DS['mod']  = pd.DataFrame(fv,  index=index)
    df_DS['ana']  = pd.DataFrame(av,  index=index)
    df_DS['misfit']  = pd.DataFrame(dv,  index=index)
    df_DS['setID']  = pd.DataFrame(setid,  index=index)
    df_DS['QC']  = pd.DataFrame(qc,  index=index)

#    # Convert tt to date
    tmp = num2date(tt, "days since 1950-01-01 00:00:00") 
    df_DS['obsdate'] = pd.DataFrame(tmp, index=index)

    print 'Accepted data number: ', len(df_DS)
    print 'Rejected data number: ', len(df_DS[df_DS['QC'] == 1])

    # Concatenate dataframes and remove rejected obs
    df_DS = df_DS[df_DS['QC'] == 0]

    # Extract SST
    df_DS_SST = df_DS[df_DS['setID'] == 40]
    df_r_list_sst.append(df_DS_SST)
    
    # Extract SST_NIGHT
    df_DS_SST_NIGHT = df_DS[df_DS['setID'] == 41]
    df_r_list_sst_night.append(df_DS_SST_NIGHT)

    # Combine data
    if len(df_DS_SST) > 0:
        df_DS_SST_combined = df_combine(df_DS_SST)
    else:
        df_DS_SST_combined = pd.DataFrame()
        df_DS_SST_combined.empty

    if len(df_DS_SST_NIGHT) > 0:
        df_DS_SST_NIGHT_combined = df_combine(df_DS_SST_NIGHT)
    else:
        df_DS_SST_NIGHT_combined = pd.DataFrame()
        df_DS_SST_NIGHT_combined.empty
    df_e_list_sst.append(df_DS_SST_combined)
    df_e_list_sst_night.append(df_DS_SST_NIGHT_combined)
    
  df_f_SST       = pd.concat(df_r_list_sst,       axis=0, ignore_index=True, copy=False)
  df_f_SST_NIGHT = pd.concat(df_r_list_sst_night, axis=0, ignore_index=True, copy=False)
  df_e_SST       = pd.concat(df_e_list_sst,       axis=0, ignore_index=True, copy=False)
  df_e_SST_NIGHT = pd.concat(df_e_list_sst_night, axis=0, ignore_index=True, copy=False)
  if len(df_e_SST):
      df_DS_SST_ensemble = combine_ensemble(df_e_SST)
  else:
      df_DS_SST_ensemble = pd.DataFrame()
      df_DS_SST_ensemble.empty
  if len(df_e_SST_NIGHT):
      df_DS_SST_NIGHT_ensemble = combine_ensemble(df_e_SST_NIGHT)
  else:
      df_DS_SST_NIGHT_ensemble = pd.DataFrame()
      df_DS_SST_NIGHT_ensemble.empty
  if len(df_f_SST):
      df_DS_SST_ensembl2 = combine_raw_ensemble(df_f_SST)
  else:
      df_DS_SST_ensembl2 = pd.DataFrame()
      df_DS_SST_ensembl2.empty
  if len(df_f_SST_NIGHT):
      df_DS_SST_NIGHT_ensembl2 = combine_raw_ensemble(df_f_SST_NIGHT)
  else:
      df_DS_SST_NIGHT_ensembl2 = pd.DataFrame()
      df_DS_SST_NIGHT_ensembl2.empty
  df_g_list_sst.append(df_DS_SST_ensemble)
  df_g_list_sst_night.append(df_DS_SST_NIGHT_ensemble)
  df_h_list_sst.append(df_DS_SST_ensembl2)
  df_h_list_sst_night.append(df_DS_SST_NIGHT_ensembl2)

df_g_SST       = pd.concat(df_g_list_sst,       axis=0, ignore_index=True, copy=False)
df_g_SST_NIGHT = pd.concat(df_g_list_sst_night, axis=0, ignore_index=True, copy=False)
df_h_SST       = pd.concat(df_h_list_sst,       axis=0, ignore_index=True, copy=False)
df_h_SST_NIGHT = pd.concat(df_h_list_sst_night, axis=0, ignore_index=True, copy=False)


if len(df_g_SST):
    df_g_cmd_SST       = combine_global(df_g_SST)
    # Treat the special case (lon_int=180,-180)
    df_grd_2_SST       = transform_180(df_g_cmd_SST)
else:
    df_grd_2_SST       = pd.DataFrame()
    df_grd_2_SST.empty


if len(df_g_SST_NIGHT):
    df_g_cmd_SST_NIGHT = combine_global(df_g_SST_NIGHT)
    # Treat the special case (lon_int=180,-180)
    df_grd_2_SST_NIGHT = transform_180(df_g_cmd_SST_NIGHT)
else:
    df_grd_2_SST_NIGHT = pd.DataFrame()
    df_grd_2_SST_NIGHT.empty


if len(df_h_SST):
   df_h_cmd_SST = combine_hlobal(df_h_SST)
   df_grd_h_SST = transform_180(df_h_cmd_SST, short=True)
else:
   df_grd_h_SST = pd.DataFrame()
   df_grd_h_SST.empty

if len(df_h_SST_NIGHT):
   df_h_cmd_SST_NIGHT = combine_hlobal(df_h_SST_NIGHT)
   df_grd_h_SST_NIGHT = transform_180(df_h_cmd_SST_NIGHT, short=True)
else:
   df_grd_h_SST_NIGHT = pd.DataFrame()
   df_grd_h_SST_NIGHT.empty

# Save dataframe to pickle object
#with open(output_dir + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_DS.pkl", "wb") as f:
#    pickle.dump(df_grd_2_SST, f, -1)
#    pickle.dump(df_grd_2_SST_NIGHT, f, -1)

df_grd_2_list = [ df_grd_2_SST, df_grd_2_SST_NIGHT]
df_grd_h_list = [ df_grd_h_SST, df_grd_h_SST_NIGHT]
type_grd_list = ['SST', 'SST_NIGHT']

for igg, df_grd_2 in enumerate(df_grd_2_list):
  type_grd=type_grd_list[igg]
  df_grd_h = df_grd_h_list[igg]
  if len(df_grd_2) > 0:
    # Plot misfit
    flds = ['new_bias', 'omb_bias']
    plot_SST_misfit_map(df_grd_2, type_grd, fld=flds)
    flds = ['gnu_bias']
    plot_SST_misfit_map(df_grd_h, type_grd, fld=flds)
    # Plot misfit rms
    flds = ['new_rmsm', 'new_rms1', 'new_rms2', 'new_estd', 'new_ostd', 'new_mstd', 'new_rmsc', 'new_rmsr']
    plot_SST_misfit_rms_map(df_grd_2, type_grd, fld=flds)
    flds = ['gnu_rmsm', 'gnu_estd', 'gnu_rmsr', 'gnu_rmst']
    plot_SST_misfit_rms_map(df_grd_h, type_grd, fld=flds)
    # Plot obs number
    plot_SST_obs_count_map(df_grd_2, type_grd, var_count='new_count')
    plot_SST_obs_count_map(df_grd_h, type_grd, var_count='gnu_count')

print 'Finished in : ', time.time()-start, ' s'

