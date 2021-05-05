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

'''
Plot DS data from netCDF ola files
'''

warnings.filterwarnings('ignore')

start = time.time()




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
        rga_IS = np.array(wk).reshape(Ndup[index], nblk).transpose()
    else:
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        if Len_bgn != 4 * Ndup[index]*jpwork_array[0,index]:
            sys.exit('records wrong::real, index = ' + str(index))
        wk = struct.unpack(">"+str(Len_bgn/4)+"f", f.read((Len_bgn/4) * 4))
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga_IS = np.array(wk).reshape(Ndup[index], jpwork_array[0,index]).transpose()
	
    # Integer part
    Len_bgn = struct.unpack(">I", f.read(4))[0]
    if Len_bgn != 4 * Ndup[index] * jpwork_array[1, index]:
        sys.exit('records wrong::int,  index = ' + str(index))
    wk = struct.unpack(">"+str(Len_bgn/4)+"i", f.read((Len_bgn/4) * 4))
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: float32')
    iga_IS = np.array(wk).reshape(Ndup[index], jpwork_array[1,index]).transpose()
    return rga_IS, iga_IS

def read_data(source_file, var):
    global Ndup, jpwork_array, TM, icycle
    fid = open(source_file, 'rb')
    [Ndup, jpwork_array, TM, icycle] = skip_header(fid)
    rga, iga = read_var(fid, var)
    fid.close()
    return rga, iga


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

    # Group data by 2deg x 2deg 
    df['lat_int'] = nearest3(query_lat, bins_lats, df['Lat'].values)
    df['lon_int'] = nearest3(query_lon, bins_lons, df['Lon'].values)

    # Bining and computing statistics
    avg   = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['lat_int', 'lon_int','misfit']]; avg.rename(columns={'misfit':'misfit_avg'}, inplace=True)
    count = df.groupby(['lat_int','lon_int'], as_index=False).count()[['misfit']]; count.rename(columns={'misfit':'obs_count'}, inplace=True)
    ms    = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['misfit_2']]; ms.rename(columns={'misfit_2':'ms'}, inplace=True)
    ms['rms'] = np.sqrt(ms['ms'].values)
    df_grd = pd.concat([avg, count, ms], axis=1)
    return df_grd

def combine_global(df):

    '''
    Combine dataframe by bining and computing stats over lat/lon
    input: raw dataframe
    output: combined dataframe
    '''
    if len(df) > 0:
        df_cmd = df.groupby(['lat_int','lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
        df_cmd['mean_bias'] = weighted_average(df, 'misfit_avg', 'obs_count', ['lat_int','lon_int'])
        df_cmd['mean_rms']  = weighted_average(df, 'rms', 'obs_count', ['lat_int','lon_int'])
    else:
        df_cmd = pd.DataFrame(np.nan, index=[], columns=[])
    return df_cmd

def weighted_average(df,data_col,weight_col,by_col):
    df['_data_times_weight'] = df[data_col]*df[weight_col]
    df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
    g = df.groupby(by_col)#, as_index=False)
    result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
    del df['_data_times_weight'], df['_weight_where_notnull']
    return result.get_values() 

def plot_SST_misfit_map(df, typ):
    '''
    Purpose: plot SST misfit map
    Arguments:
    df: dataframe containing data
    '''
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
    colors = plt.cm.coolwarm(norm(df['new_bias'].values))
    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
    clevs = np.linspace(-1.0, 1.0, 20)
    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
    ticks = [-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
    c.ax.tick_params(labelsize=12)
    if typ == 'SST':
        plt.savefig(output_dir +'/GEN_SST_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png')
    elif typ == 'SST_NIGHT':
        plt.savefig(output_dir +'/GEN_SST_NIGHT_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png')


def plot_SST_misfit_rms_map(df, typ):
    '''
    Purpose: plot SST misfit RMS map
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
        plt.title(suite_name + ': SST average misfit rms in deg', fontsize=16)
    elif typ == 'SST_NIGHT':
        plt.title(suite_name + ': SST_NIGHT average misfit rms in deg', fontsize=16)

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
    colors = [cmap(normalize(v)) for v in df['new_rms'].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max', format='%.1f')
    c.ax.tick_params(labelsize=12)
    if typ == 'SST':
        plt.savefig(output_dir +'/GEN_SST_' + sdate + '_' + fdate + '_RMS_MISFIT_map.png')
    elif typ == 'SST_NIGHT':
        plt.savefig(output_dir +'/GEN_SST_NIGHT_' + sdate + '_' + fdate + '_RMS_MISFIT_map.png')
   

def plot_SST_obs_count_map(df, typ):
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
    normalize = matplotlib.colors.Normalize(vmin=0., vmax=np.percentile(df['new_count'].values, 90))
    colors = [cmap(normalize(v)) for v in df['new_count'].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max')
    c.ax.tick_params(labelsize=12)
    if typ == 'SST':
        plt.savefig(output_dir +'/GEN_SST_' + sdate + '_' + fdate + '_NUM_DATA_map.png')
    elif typ == 'SST_NIGHT':
        plt.savefig(output_dir +'/GEN_SST_NIGHT_' + sdate + '_' + fdate + '_NUM_DATA_map.png')


def transform_180(df):
    df_ = df.copy()
    df_['lon_int'][df_['lon_int'] == -180] = 180
    xx = df_.groupby(['lat_int', 'lon_int'], as_index=False).sum()[['lat_int','lon_int','obs_count']]
    xx.rename(columns={'obs_count':'new_count'}, inplace=True)
    yy = df_.groupby(['lat_int', 'lon_int'], as_index=False).mean()[['mean_bias']]
    yy.rename(columns={'mean_bias':'new_bias'}, inplace=True)
    zz = df_.groupby(['lat_int', 'lon_int'], as_index=False).mean()[['mean_rms']]
    zz.rename(columns={'mean_rms':'new_rms'}, inplace=True)
    df_ = pd.concat([xx, yy, zz], axis=1)
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

suite_name   = ap.parse_args().suite
input_dir    = ap.parse_args().input_dir
output_dir   = ap.parse_args().output_dir
sdate        = ap.parse_args().start_date
fdate        = ap.parse_args().final_date
exp_id       = ap.parse_args().stype

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
for num_dates in range(len(dates)):
    dateS = datetime.datetime.strftime(dates[num_dates], "%Y%m%d")
    print 'Working on date: ', dateS

    if os.path.exists(input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz'):                # case where file is zipped
        os.system('rm -rf /home/kch001/ords/tempo/*')
        os.system('cp ' + input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola.gz /home/kch001/ords/tempo/')
        os.system('gunzip /home/kch001/ords/tempo/' + dateS + '00_SAM.ola.gz')
        input_file = '/home/kch001/ords/tempo/' + dateS + '00_SAM.ola'
    else: # case where file is not zipped
        input_file = input_dir + '/' + dateS + '/DIA/' + dateS + '00_SAM.ola'

    # Read DS data
    rga_DS, iga_DS = read_data(input_file, 'DS')

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
    
    # Extract SST_NIGHT
    df_DS_SST_NIGHT = df_DS[df_DS['setID'] == 41]

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


    df_g_list_sst.append(df_DS_SST_combined)
    df_g_list_sst_night.append(df_DS_SST_NIGHT_combined)

df_g_SST       = pd.concat(df_g_list_sst,       axis=0, ignore_index=True, copy=False)
df_g_SST_NIGHT = pd.concat(df_g_list_sst_night, axis=0, ignore_index=True, copy=False)


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


# Save dataframe to pickle object
with open(output_dir + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_DS.pkl", "wb") as f:
    pickle.dump(df_grd_2_SST, f, -1)
    pickle.dump(df_grd_2_SST_NIGHT, f, -1)



if len(df_grd_2_SST) > 0:
    # Plot misfit
    plot_SST_misfit_map(df_grd_2_SST, 'SST')
    # Plot misfit rms
    plot_SST_misfit_rms_map(df_grd_2_SST, 'SST')
    # Plot obs number
    plot_SST_obs_count_map(df_grd_2_SST, 'SST')

if len(df_grd_2_SST_NIGHT) > 0:
    # Plot misfit
    plot_SST_misfit_map(df_grd_2_SST_NIGHT, 'SST_NIGHT')
    # Plot misfit rms
    plot_SST_misfit_rms_map(df_grd_2_SST_NIGHT, 'SST_NIGHT')
    # Plot obs number
    plot_SST_obs_count_map(df_grd_2_SST_NIGHT, 'SST_NIGHT')


print 'Finished in : ', time.time()-start, ' s'

