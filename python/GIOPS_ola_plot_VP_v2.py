'''
Script purpose:
Read ola files, compute statistics over bin of 2x2 degrees and different depth ranges ([0-50m], [0-500m] and [500-2000m])
Produce graphics for average msifit [O-P], misfit rms and mean obs number
'''

import argparse
import struct
import os
import sys
import getopt
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
from collections import OrderedDict
import cPickle as pickle


def skip_header(f):
    """
    Function that skips the header and reads some needed information
    Input: Input file Identifier defined in main script
    Output: [Ndup, jpwork_array, TM, icycle] ..TO DEFINE LATER
    """
    for _ in range(20):
        header_length_bytes = f.read(4)
        nbytes = struct.unpack(">I", header_length_bytes)[0]
        f.seek(nbytes + 4, os.SEEK_CUR)
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print Len_bgn
    icycle  = struct.unpack(">I", f.read(4))[0] #;  print icycle
    TM      = struct.unpack(">3d", f.read(3 * 8)) #; print TM
    Len_end = struct.unpack(">I", f.read(4))[0] #; print Len_end
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: TM')
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print Len_bgn
    Ndup    = struct.unpack(">4I", f.read(4 * 4)) #; print Ndup 
    jpwork_array = struct.unpack(">8I", f.read(8 * 4)) #; print jpwork_array
    jpwork_array = np.array(jpwork_array).reshape(4,2).transpose() #; print jpwork_array
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: Ndup')
    return [Ndup, jpwork_array, TM, icycle]


def read_var(f, var):
    print 'Reading data for DUP_id = ', var
    index = family.index(var.upper())
    for _ in range(index):
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
    # Real part
    if var.upper() == 'IS':
        print 'We removed Hr in DUP_IS'
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        nblk = 12
        skip_Hr = 4 * (jpwork_array[0, index] - nblk)
        wk=[]
        for i in range(Ndup[index]):
            wk.extend(struct.unpack(">"+str(nblk)+"f", f.read(nblk * 4)))
            f.seek(skip_Hr, os.SEEK_CUR)
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], nblk).transpose()
    else:
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        if Len_bgn != 4 * Ndup[index]*jpwork_array[0,index]:
            sys.exit('records wrong::real, index = ' + str(index))
        wk = struct.unpack(">"+str(Len_bgn/4)+"f", f.read((Len_bgn/4) * 4))
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], jpwork_array[0,index]).transpose()
	
    # Integer part
    Len_bgn = struct.unpack(">I", f.read(4))[0]
    if Len_bgn != 4 * Ndup[index] * jpwork_array[1, index]:
        sys.exit('records wrong::int,  index = ' + str(index))
    wk = struct.unpack(">"+str(Len_bgn/4)+"i", f.read((Len_bgn/4) * 4))
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: float32')
    iga = np.array(wk).reshape(Ndup[index], jpwork_array[1,index]).transpose()
    return rga, iga

def read_data(source_file, var):
    global Ndup, jpwork_array, TM, icycle
    fid = open(source_file, 'rb')
    [Ndup, jpwork_array, TM, icycle] = skip_header(fid)
    rga, iga = read_var(fid, var)
    fid.close()
    return rga, iga

def nearest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before

def nearest2(myList, myNumbers):
    myList = np.array(myList)
    myNumbers = np.array(myNumbers) 
    myList.shape = myList.shape + (1,)
    myNumbers.shape = myNumbers.shape + (1,)
    t = KDTree(myList)
    dists, inds = t.query(myNumbers)
    return myList[inds]  


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

def df_combine(df, depth1, depth2):
    '''
    Combine, groupby and compute stististics 
    Input: df: pandas Dataframe produced through the reading loop
           depth1, depth2: depth limits (floats)
    Output: combined dataframe
    '''
    # Keep only data between depth1 and depth2
    df_g = df[(df['depth_T'] >= depth1) & (df['depth_T'] <= depth2) & (df['depth_S'] >= depth1) & (df['depth_S'] <= depth2)]
    if len(df_g) == 0:
        return 
    df_g['lat_int'] = nearest3(query_lat, bins_lats, df_g['lat'].values)
    df_g['lon_int'] = nearest3(query_lon, bins_lons, df_g['lon'].values)
    df_g['depth-mid'] = np.repeat((depth2-depth1)/2.0, len(df_g))  
    df_g['misfitT2'] = df_g['misfitT'].values **2 
    df_g['misfitS2'] = df_g['misfitS'].values **2
    # Temperature
    avg_T = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).mean()[['lat_int', 'lon_int', 'misfitT']]
    avg_T.rename(columns={'misfitT': 'misfit_T_avg'}, inplace=True)
    count_T = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).count()[['misfitT']]
    count_T.rename(columns={'misfitT': 'obs_count_T'}, inplace=True)
    ms_T = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).mean()[['misfitT2']]
    ms_T.rename(columns={'misfitT2': 'ms_T'}, inplace=True)
    ms_T['rms_T'] = np.sqrt(ms_T['ms_T'].values)
    # Salinity
    avg_S = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).mean()[['misfitS']]
    avg_S.rename(columns={'misfitS': 'misfit_S_avg'}, inplace=True)
    count_S = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).count()[['misfitS']]
    count_S.rename(columns={'misfitS': 'obs_count_S'}, inplace=True)
    ms_S = df_g.groupby(['lat_int', 'lon_int', 'depth-mid'], as_index=False).mean()[['misfitS2']]
    ms_S.rename(columns={'misfitS2': 'ms_S'}, inplace=True)
    ms_S['rms_S'] = np.sqrt(ms_S['ms_S'].values)
    
    df_g_grd = pd.concat([avg_T, count_T, ms_T, avg_S, count_S, ms_S], axis=1)
    # Add a date column
    df_g_grd['date'] = [dateS] * len(df_g_grd)  
    return df_g_grd


def weighted_average(df, data_col, weight_col, by_col):
    df['_data_times_weight'] = df[data_col]*df[weight_col]
    df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
    g = df.groupby(by_col)
    result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
    del df['_data_times_weight'], df['_weight_where_notnull']
    return result.get_values() 

def transform_180(df, var):
    '''
    Purpose:
    Perform the bining for the special case lon=-180
    Input: 
        df: dataframe containg data
        var: variable string ('temperature or 'salinity')
    '''
    df_ = df.copy()
    df_['lon_int'][df_['lon_int'] == -180] = 180
    if var.lower() == 'temperature':
        xx = df_.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
        xx.rename(columns={'obs_count_T': 'new_count_T'}, inplace=True)
    if var.lower() == 'salinity':
        xx = df_.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
        xx.rename(columns={'obs_count_S': 'new_count_S'}, inplace=True)
    
    yy = df_.groupby(['lat_int', 'lon_int'], as_index=False).mean()[['mean_bias']]
    yy.rename(columns={'mean_bias': 'new_bias'}, inplace=True)
    zz = df_.groupby(['lat_int', 'lon_int'], as_index=False).mean()[['mean_rms']]
    zz.rename(columns={'mean_rms': 'new_rms'}, inplace=True)
    df_ = pd.concat([xx, yy, zz], axis=1)
    return df_


def plot_VP_misfit_map(df, dep, var):
    '''
    Purpose: plot VP misfit map
    Arguments:
    df: dataframe containing data
    depth: 500 or 50
    var: 'temperature' or 'salinity'
    '''
    #suite_name='GIOPSv2' # exception    
    print dep, var[0].upper()+var[1:].lower()
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=180, resolution='c')
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    df['lon_int'][df['lon_int'] < 0] += 360                
    x, y = m(df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    if dep == 500:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-500m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-500m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 50:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-50m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-50m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 2000:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [500-2000m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [500-2000m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 10:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-10m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-10m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 5:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-5m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-5m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    else:
        sys.exit('plot_VP_misfit_map: The depth argument is not correct!')
        
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90., 91., 30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(0., 361., 45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    if var.lower() == 'temperature':
        vmin, vmax = -1.0, 1.0
    if var.lower() == 'salinity':
        vmin, vmax = -0.5, 0.5
    norm = matplotlib.colors.Normalize(vmin = vmin, vmax = vmax, clip = False)
    colors = plt.cm.coolwarm(norm(df['new_bias'].values))
    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
    if var.lower() == 'temperature':
        clevs = np.arange(-1.0,1.1,0.1)
        ticks = clevs[::2]
    if var.lower() == 'salinity':
        clevs = np.arange(-0.5, 0.51, 0.05)
        ticks = [-0.50, -0.33, -0.17, 0.00, 0.17, 0.33, 0.50]
    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
    c.ax.tick_params(labelsize=12)
    plt.savefig(output_path +'/INSITU_' + sdate + '_' + fdate + '_' + var.upper() + '_AVR_MISFIT_map_'+ str(dep) + '.png')


def plot_VP_misfit_rms_map(df, dep, var):
    '''
    Purpose: plot VP misfit RMS map
    Arguments:
    df: dataframe containing data
    depth: 500 or 50
    var: 'temperature' ou 'salinity' 
    '''
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=190, resolution='c')
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    df['lon_int'][df['lon_int'] < 0] += 360                
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)); ax = fig.gca() 
    #fig = plt.figure(figsize=(8, 8)); ax = fig.gca() 
    if dep == 500:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit rms in deg [0-500m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit rms in PSU [0-500m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_rms_map:  Something wrong with var argument ..')
    elif dep == 50:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit rms in deg [0-50m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit rms in PSU [0-50m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_rms_map:  Something wrong with var argument ..')
    elif dep == 2000:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [500-2000m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [500-2000m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 10:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-10m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-10m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 5:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': Temperature average misfit in deg [0-5m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': Salinity average misfit in PSU [0-5m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    else:
        sys.exit('plot_VP_misfit_rms_map: The depth argument is not correct!')
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    cmap = matplotlib.cm.get_cmap('jet')
    if var.lower() == 'temperature':
        vmin, vmax = 0., 2.0
        ticks = [0., 0.33, 0.67, 1.0, 1.33, 1.67, 2.0]
    if var.lower() == 'salinity':
        vmin, vmax = 0., 0.5
        ticks = [0., 0.08, 0.17, 0.25, 0.33, 0.42, 0.5]
    normalize = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    colors = [cmap(normalize(v)) for v in df['new_rms'].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max', ticks=ticks, format='%.2f')
    c.ax.tick_params(labelsize=12)
    plt.savefig(output_path + '/INSITU_' + sdate + '_' + fdate + '_' + var.upper() + '_RMS_MISFIT_map_' + str(dep) + '.png')

def plot_VP_obs_count_map(df, dep, var):
    '''
    Purpose: plot VP obs number map
    Arguments:
    df: dataframe containing data
    depth: 500 or 50
    var: temperature ou salinity
    '''
    #suite_name='GIOPSv2' # exception    
    if var == 'temperature':
        col_name = 'new_count_T'
    elif var == 'salinity':
        col_name = 'new_count_S'
    else:
        sys.exit('Variable name not correct')
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=180, resolution='c')
    df['lon_int'][df['lon_int'] < 0] += 360                
    x, y = m(df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    if dep == 500:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': VP temperature observations number [0-500m]', fontsize=16)
        if var.lower() == 'salinity':
            plt.title(suite_name + ': VP salinity observations number [0-500m]', fontsize=16)
        
    elif dep == 50:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': VP temperature observations number [0-50m]', fontsize=16)
        if var.lower() == 'salinity':
            plt.title(suite_name + ': VP salinity observations number [0-50m]', fontsize=16)
    
    elif dep == 2000:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': VP temperature observations number [500-2000m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': VP salinity observations number [500-2000m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 10:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': VP temperature observations number [0-10m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': VP salinity observations number [0-10m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 5:
        if var.lower() == 'temperature':
            plt.title(suite_name + ': VP temperature observations number [0-5m]', fontsize=16)
        elif var.lower() == 'salinity':
            plt.title(suite_name + ': VP salinity observations number [0-5m]', fontsize=16)
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    else:
        print('The depth argument is not correct!')
        sys.exit(2)
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    cmap = matplotlib.cm.get_cmap('YlOrRd')
    normalize = matplotlib.colors.Normalize(vmin=0., vmax=np.percentile(df[col_name].values, 90))
    colors = [cmap(normalize(v)) for v in df[col_name].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max')
    c.ax.tick_params(labelsize=12)
    plt.savefig(output_path + '/INSITU_' + sdate + '_' + fdate + '_' + var.upper() + '_NUM_DATA_map_' + str(dep) + '.png')
    


# Model levels depths
depth = np.loadtxt('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_depths')

jpk = len(depth)  # Model levels number

nlevs = jpk - 1      # Considered levels
maxMVS = (jpk-1)*2   # Maximum levels number
ip_jkdta_TEM = 2     # the first index for SST, only for present and before GIOPS300b

depth = np.concatenate((depth[1:], depth[1:]))

family = ['IS','VP','UV','DS']

global Ndup, jpwork_array, TM, icycle


# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",      required=True, help="Experiment name")
ap.add_argument("--input_dir",  required=True, help="Input directory for experiment")
ap.add_argument("--output_dir", required=True, help="Analysis date")
ap.add_argument("--start_date", required=True, help="Start date")
ap.add_argument("--final_date", required=True, help="Final date")


suite_name  = ap.parse_args().suite
input_dir   = ap.parse_args().input_dir
output_path = ap.parse_args().output_dir
sdate       = ap.parse_args().start_date
fdate       = ap.parse_args().final_date

start_date = datetime.datetime.strptime(sdate, "%Y%m%d")
final_date = datetime.datetime.strptime(fdate, "%Y%m%d")


# Make sure dates are in order
if start_date > final_date:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)


# Print entered arguments
print 'Experiment name: ', suite_name
print 'Start date: ', sdate
print 'End date:   ', fdate


# Create output folder
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not output_path.endswith('/'):
    output_path = output_path + '/'

# Number of dates during the cycle
num_days = (final_date - start_date).days
# List of dates of the cycle
dates = [start_date + datetime.timedelta(days=x) for x in range(0, num_days + 7, 7)]


#Initialize the dataframes list
df_global_list_500  = []
df_global_list_50  = []
df_global_list_500_2000  = []
df_global_list_10 = []
df_global_list_5 = []

# Define lats and lons for 2x2 bins
bins_lons = np.arange(-180, 181, 2)  
bins_lats = np.arange(-90, 91, 2)
xlon = bins_lons
xlon.shape = bins_lons.shape + (1,)
xlat = bins_lats
xlat.shape = bins_lats.shape + (1,)
query_lon = cKDTree(xlon)
query_lat = cKDTree(xlat)

pd.options.mode.chained_assignment = None

start0 = time.time()

tmpdir = '/home/kch001/ords/tempo/' + suite_name + '/'
os.system('mkdir -p ' + tmpdir)

for num_dates in range(len(dates)):
    dateS = datetime.datetime.strftime(dates[num_dates], "%Y%m%d")
    print 'Working on date: ', dateS

    if os.path.exists(input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz'):                # case where file is zipped
        os.system('rm -rf ' + tmpdir + '*')
        os.system('cp ' + input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz ' + tmpdir)
        os.system('gunzip ' + tmpdir + dateS + '00_SAM.ola.gz')
        input_file = tmpdir + dateS + '00_SAM.ola'
    else: # case where file is not zipped
        input_file = input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola'

    rga_VP, iga_VP = read_data(input_file, 'VP')

#    with Dataset(input_file, 'r') as f:
#        rga_VP = f.variables['rga_VP'][:]
#        iga_VP = f.variables['iga_VP'][:]
    nv, nprf = rga_VP.shape

    if (nv != maxMVS*5+7):  
        print('Wrong dimension: nv in rga_VP')
        sys.exit(2)
    
    ni, nprf = iga_VP.shape
    if (ni != maxMVS*2+11):   # for GIOPSv3
    #if (ni != maxMVS*2+10):   # for GIOPSv2
        print('Wrong dimension: ni in iga_VP')
        sys.exit(2)
    #Initialization
    df_g = pd.DataFrame(np.nan, index=[], columns=[])
    vo = np.empty((maxMVS, nprf)) * np.nan
    vf = np.empty((maxMVS, nprf)) * np.nan
    dv = np.empty((maxMVS, nprf)) * np.nan
    dep = np.empty((maxMVS, nprf)) * np.nan
    start = time.time()
    df_list = []
    
    for pr in range(nprf):
        nmvs = iga_VP[9, pr]
        idx = np.arange(nmvs)
        kk = iga_VP[idx+10, pr] - ip_jkdta_TEM
        if kk.max() >= maxMVS:
            print "problem with this date: {0} and profile: {1}".format(dateS, pr)
            continue
        kk = kk[iga_VP[idx+10+maxMVS, pr] == 0].tolist()
        vo[kk, pr] = rga_VP[idx+3, pr]
        vf[kk, pr] = rga_VP[idx+3+maxMVS*1, pr]
        dv[kk, pr] = rga_VP[idx+3+maxMVS*3, pr]
        dep[kk, pr] = depth[kk]
        vo_T = vo[:maxMVS/2, pr]
        vo_S = vo[maxMVS/2:, pr]
        vf_T = vf[:maxMVS/2, pr]
        vf_S = vf[maxMVS/2:, pr]
        dv_T = dv[:maxMVS/2, pr]
        dv_S = dv[maxMVS/2:, pr]
        lon = np.repeat(np.array(rga_VP[0, pr]), nlevs)
        lat = np.repeat(np.array(rga_VP[1, pr]), nlevs)
        date = np.repeat(np.array(rga_VP[2, pr]), nlevs) 
        depth_T = dep[:maxMVS/2, pr]
        depth_S = dep[maxMVS/2:, pr]
        dic = OrderedDict([('lon', lon),
                           ('lat', lat),
                           ('depth_T', depth_T),
                           ('depth_S', depth_S),  
                           ('date', date),
                           ('voT', vo_T),
                           ('voS', vo_S),
                           ('vfT', vf_T),
                           ('vfS', vf_S),
                           ('misfitT', dv_T),
                           ('misfitS', dv_S)])
        df = pd.DataFrame.from_dict(dic)
        del dic
        df_list.append(df)
    print "Date: {0}  Found : {1} profiles   Treated in {2} s".format(dateS, nprf, time.time()-start)    
    
    df_g = pd.concat(df_list, axis=0, ignore_index=True, copy=False)
    df_g_500_grd = df_combine(df_g, 0., 500.)
    df_g_50_grd = df_combine(df_g, 0., 50.)
    df_g_500_2000_grd = df_combine(df_g, 500., 2000.)
    df_g_0_10_grd = df_combine(df_g, 0, 10.)
    df_g_0_5_grd = df_combine(df_g, 0, 5.)

    df_global_list_500.append(df_g_500_grd)
    df_global_list_50.append(df_g_50_grd)
    df_global_list_500_2000.append(df_g_500_2000_grd)
    df_global_list_10.append(df_g_0_10_grd)
    df_global_list_5.append(df_g_0_5_grd)

#Combine global dataframes
df_global_500 = pd.concat(df_global_list_500, axis=0, ignore_index=True, copy=False)   # First 500m 
df_global_50 = pd.concat(df_global_list_50 , axis=0, ignore_index=True, copy=False)   # First 50m
df_global_500_2000  = pd.concat(df_global_list_500_2000 , axis=0, ignore_index=True, copy=False)   # between 500 and 2000m 
df_global_10 = pd.concat(df_global_list_10 , axis=0, ignore_index=True, copy=False)   # First 10m
df_global_5 = pd.concat(df_global_list_5 , axis=0, ignore_index=True, copy=False)   # First 5m

# 5m
# Temperature
T_data_5 = df_global_5.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
T_data_5['mean_bias'] = weighted_average(df_global_5, 'misfit_T_avg', 'obs_count_T', ['lat_int', 'lon_int'])
T_data_5['mean_rms'] = weighted_average(df_global_5, 'rms_T', 'obs_count_T', ['lat_int','lon_int'])

# Salinity
S_data_5 = df_global_5.groupby(['lat_int','lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
S_data_5['mean_bias'] = weighted_average(df_global_5, 'misfit_S_avg', 'obs_count_S', ['lat_int', 'lon_int'])
S_data_5['mean_rms'] = weighted_average(df_global_5, 'rms_S', 'obs_count_S', ['lat_int', 'lon_int'])

# 10m
# Temperature
T_data_10 = df_global_10.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
T_data_10['mean_bias'] = weighted_average(df_global_10, 'misfit_T_avg', 'obs_count_T', ['lat_int', 'lon_int'])
T_data_10['mean_rms'] = weighted_average(df_global_10, 'rms_T', 'obs_count_T', ['lat_int', 'lon_int'])

# Salinity
S_data_10 = df_global_10.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
S_data_10['mean_bias'] = weighted_average(df_global_10, 'misfit_S_avg', 'obs_count_S', ['lat_int', 'lon_int'])
S_data_10['mean_rms'] = weighted_average(df_global_10, 'rms_S', 'obs_count_S', ['lat_int', 'lon_int'])

# 500m
# Temperature
T_data_500 = df_global_500.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
T_data_500['mean_bias'] = weighted_average(df_global_500, 'misfit_T_avg', 'obs_count_T', ['lat_int', 'lon_int'])
T_data_500['mean_rms'] = weighted_average(df_global_500, 'rms_T', 'obs_count_T', ['lat_int', 'lon_int'])

# Salinity
S_data_500 = df_global_500.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
S_data_500['mean_bias'] = weighted_average(df_global_500, 'misfit_S_avg', 'obs_count_S', ['lat_int', 'lon_int'])
S_data_500['mean_rms'] = weighted_average(df_global_500, 'rms_S', 'obs_count_S', ['lat_int', 'lon_int'])

# 50m
# Temperature
T_data_50 = df_global_50.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
T_data_50['mean_bias'] = weighted_average(df_global_50, 'misfit_T_avg', 'obs_count_T', ['lat_int', 'lon_int'])
T_data_50['mean_rms'] = weighted_average(df_global_50, 'rms_T', 'obs_count_T', ['lat_int', 'lon_int'])

# Salinity
S_data_50 = df_global_50.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
S_data_50['mean_bias'] = weighted_average(df_global_50, 'misfit_S_avg', 'obs_count_S', ['lat_int', 'lon_int'])
S_data_50['mean_rms'] = weighted_average(df_global_50, 'rms_S', 'obs_count_S', ['lat_int', 'lon_int'])

# 500-2000m
# Temperature
T_data_500_2000 = df_global_500_2000.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_T']]
T_data_500_2000['mean_bias'] = weighted_average(df_global_500_2000, 'misfit_T_avg', 'obs_count_T', ['lat_int', 'lon_int'])
T_data_500_2000['mean_rms'] = weighted_average(df_global_500_2000, 'rms_T', 'obs_count_T', ['lat_int', 'lon_int'])

# Salinity
S_data_500_2000 = df_global_500_2000.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int', 'lon_int', 'obs_count_S']]
S_data_500_2000['mean_bias'] = weighted_average(df_global_500_2000, 'misfit_S_avg', 'obs_count_S', ['lat_int', 'lon_int'])
S_data_500_2000['mean_rms'] = weighted_average(df_global_500_2000, 'rms_S', 'obs_count_S', ['lat_int', 'lon_int'])



# Perform bining for the case of lon=-180
T_data_5_ = transform_180(T_data_5, 'temperature')
S_data_5_ = transform_180(S_data_5, 'salinity')
T_data_10_ = transform_180(T_data_10, 'temperature')
S_data_10_ = transform_180(S_data_10, 'salinity')
T_data_50_ = transform_180(T_data_50, 'temperature')
S_data_50_ = transform_180(S_data_50, 'salinity')
T_data_500_ = transform_180(T_data_500, 'temperature')
S_data_500_ = transform_180(S_data_500, 'salinity')
T_data_500_2000_ = transform_180(T_data_500_2000, 'temperature')
S_data_500_2000_ = transform_180(S_data_500_2000, 'salinity')

print "Dates loop finished in: {0}".format(time.time() - start0)

# Save dataframes to pickle objects

with open(output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_VP_T.pkl", 'wb') as fT:
  pickle.dump(T_data_5_, fT, -1)
  pickle.dump(T_data_10_, fT, -1)
  pickle.dump(T_data_50_, fT, -1)
  pickle.dump(T_data_500_, fT, -1)
  pickle.dump(T_data_500_2000_, fT, -1)
fT.close

with open(output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_VP_S.pkl", 'wb') as fS:
  pickle.dump(S_data_5_, fS, -1)
  pickle.dump(S_data_10_, fS, -1)
  pickle.dump(S_data_50_, fS, -1)
  pickle.dump(S_data_500_, fS, -1)
  pickle.dump(S_data_500_2000_, fS, -1)
fS.close

# Producing plots
#Temperature
plot_VP_misfit_map(T_data_5_, 5, 'temperature')
plot_VP_misfit_map(T_data_10_, 10, 'temperature')
plot_VP_misfit_map(T_data_50_, 50, 'temperature')
plot_VP_misfit_map(T_data_500_, 500, 'temperature')
plot_VP_misfit_map(T_data_500_2000_, 2000, 'temperature')
plot_VP_misfit_rms_map(T_data_5_, 5, 'temperature')
plot_VP_misfit_rms_map(T_data_10_, 10, 'temperature')
plot_VP_misfit_rms_map(T_data_50_, 50, 'temperature')
plot_VP_misfit_rms_map(T_data_500_, 500, 'temperature')
plot_VP_misfit_rms_map(T_data_500_2000_, 2000, 'temperature')
plot_VP_obs_count_map(T_data_5_, 5, 'temperature')
plot_VP_obs_count_map(T_data_10_, 10, 'temperature')
plot_VP_obs_count_map(T_data_50_, 50, 'temperature')
plot_VP_obs_count_map(T_data_500_, 500, 'temperature')
plot_VP_obs_count_map(T_data_500_2000_, 2000, 'temperature')

#Salinity
plot_VP_misfit_map(S_data_5_, 5, 'salinity')
plot_VP_misfit_map(S_data_10_, 10, 'salinity')
plot_VP_misfit_map(S_data_50_, 50, 'salinity')
plot_VP_misfit_map(S_data_500_, 500, 'salinity')
plot_VP_misfit_map(S_data_500_2000_, 2000, 'salinity')
plot_VP_misfit_rms_map(S_data_5_, 5, 'salinity')
plot_VP_misfit_rms_map(S_data_10_, 10, 'salinity')
plot_VP_misfit_rms_map(S_data_50_, 50, 'salinity')
plot_VP_misfit_rms_map(S_data_500_, 500, 'salinity')
plot_VP_misfit_rms_map(S_data_500_2000_, 2000, 'salinity')
plot_VP_obs_count_map(S_data_5_, 5, 'salinity')
plot_VP_obs_count_map(S_data_10_, 10, 'salinity')
plot_VP_obs_count_map(S_data_50_, 50, 'salinity')
plot_VP_obs_count_map(S_data_500_, 500, 'salinity')
plot_VP_obs_count_map(S_data_500_2000_, 2000, 'salinity')

