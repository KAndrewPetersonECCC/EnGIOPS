'''
Script purpose:
Read ola, bin data on 2x2 degrees, compute statistics and produce graphics for:
 -- Mean misfit [O-P] 
 -- Misfit rms
 -- Mean obs number

'''
import struct
import argparse
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
import cPickle as pickle

'''
Plot IS data from netCDF ola files
'''

warnings.filterwarnings('ignore')

start = time.time()


# Functions definition

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
    
    df['misfit_cm']  = df['misfit'].values *100         # convert to cm
    df['misfit_cm2'] = df['misfit_cm'].values **2       # square

    df['lat_int'] = nearest3(query_lat, bins_lats, df['Lat'].values)
    df['lon_int'] = nearest3(query_lon, bins_lons, df['Lon'].values)

    avg   = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['lat_int', 'lon_int','misfit_cm']]; avg.rename(columns={'misfit_cm':'misfit_avg'}, inplace=True)
    count = df.groupby(['lat_int','lon_int'], as_index=False).count()[['misfit_cm']]; count.rename(columns={'misfit_cm':'obs_count'}, inplace=True)
    ms    = df.groupby(['lat_int','lon_int'], as_index=False).mean()[['misfit_cm2']]; ms.rename(columns={'misfit_cm2':'ms'}, inplace=True)
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
    g = df.groupby(by_col)
    result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
    del df['_data_times_weight'], df['_weight_where_notnull']
    return result.get_values() 
    
def transform_180(df):
    '''
    Purpose:
    Performs the bining for the special case of lon=-180 deg
    '''
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

    

def plot_SLA_misfit_map(df, inst):
    '''
    Purpose: plot SLA misfit map
    Arguments:
    df: dataframe containing data
    inst: string defining the instrument (satellite)
          ALL (all satellites), 
          'ALTIKA', 
          'CRYOSAT2', 
          'CRYOSAT2N', 
          'JASON2', 
          'JASON3', 
          'JASON2N', 
          'HY2A', 
          'SENTINEL3A',
          'SENTINEL3B'
    '''
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    df['lon_int'][df['lon_int'] < 0] += 360                
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    #fig = plt.figure(figsize=(8, 8)) 
    plt.title(suite_name + ': Average misfit for ' + inst + ' SLA observations in cm', fontsize=16)
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)

    norm = matplotlib.colors.Normalize(vmin = -10, vmax = 10, clip = False)
    colors = plt.cm.coolwarm(norm(df['new_bias'].values))
    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
    clevs = np.arange(-10.5,11,1)
    ticks = np.arange(-10, 11, 2)
    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
    cmap.set_bad(color='black')
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
    c.ax.tick_params(labelsize=12)

    plt.savefig(output_path +'/' + inst + '_' + sdate + '_' + fdate + '_AVR_MISFIT_map.png')


def plot_SLA_misfit_rms_map(df, inst):
    '''
    Purpose: plot SLA misfit RMS map
    Arguments:
    df: dataframe containing data
    inst: string defining the instrument (satellite) used
          ALL (all satellites), 
          'ALTIKA', 
          'CRYOSAT2', 
          'CRYOSAT2N', 
          'JASON2', 
          'JASON3', 
          'JASON2N', 
          'HY2A', 
          'SENTINEL3A',
          'SENTINEL3B'
    '''
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
#    m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    df['lon_int'][df['lon_int'] < 0] += 360 
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    #fig = plt.figure(figsize=(8, 8)) 
    fig = plt.figure(figsize=(10, 6)) 
    plt.title(suite_name + ': Average misfit rms for ' + inst + ' SLA observations in cm', fontsize=16)
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)
    cmap = matplotlib.cm.get_cmap('jet')
    normalize = matplotlib.colors.Normalize(vmin=0., vmax=30.)
    colors = [cmap(normalize(v)) for v in df['new_rms'].values]
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, ax=ax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='max')
    c.ax.tick_params(labelsize=12)
    plt.savefig(output_path +'/' + inst + '_' + sdate + '_' + fdate + '_RMS_MISFIT_map.png') # Kamel

def plot_SLA_obs_count_map(df, inst):
    '''
    Purpose: plot SLA obs number map
    Arguments:
    df: dataframe containing data
    inst: string defining the instrument (satellite) used
          ALL (all satellites), 
          'ALTIKA', 
          'CRYOSAT2', 
          'CRYOSAT2N', 
          'JASON2', 
          'JASON3', 
          'JASON2N', 
          'HY2A', 
          'SENTINEL3A',
          'SENTINEL3B'
    '''
#    m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=180, resolution='c')
    df['lon_int'][df['lon_int'] < 0] += 360
    x, y = m(df['lon_int'].values, df['lat_int'].values)
    #fig = plt.figure(figsize=(8, 8)) 
    fig = plt.figure(figsize=(10, 6)) 
    plt.title(suite_name + ': Obs number for ' + inst + ' SLA observations', fontsize=16)
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
    plt.savefig(output_path +'/' + inst + '_' + sdate + '_' + fdate + '_NUM_DATA_map.png')


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
output_path  = ap.parse_args().output_dir
sdate        = ap.parse_args().start_date
fdate        = ap.parse_args().final_date
exp_id       = ap.parse_args().stype

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
if exp_id.upper() == 'W':
    dates = [start_date + datetime.timedelta(days=x) for x in range(0, num_days + 7, 7)]
elif exp_id.upper() == 'D':
    dates = [start_date + datetime.timedelta(days=x) for x in range(0, num_days + 1)]

# Create empty lists to fill in through the time loop

df_AL_list = []
df_C2_list = []
df_C2_list = []
df_J2_list = []
df_J3_list = []
df_J2N_list = []
df_H2_list = []
df_S3A_list = []
df_ALL_list = []

# Define lats and lons for 2x2 bins
bins_lons = np.arange(-180, 181, 2) # Kamel
bins_lats = np.arange(-90, 91, 2)
xlon = bins_lons ; xlon.shape = bins_lons.shape + (1,)
xlat = bins_lats ; xlat.shape = bins_lats.shape + (1,)
query_lon = cKDTree(xlon)
query_lat = cKDTree(xlat)

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

    rga_IS, iga_IS = read_data(input_file, 'IS')
    
#    with Dataset(input_file, 'r') as f:
#        rga_IS = f.variables['rga_IS'][:]
#        iga_IS = f.variables['iga_IS'][:]

    # Extract variables and build dataframe

    lon = rga_IS[0, :]        # Longitude
    lat = rga_IS[1, :]        # Latitude
    tt  = rga_IS[2, :]        # Time (days since 1950-01-01 00:00:00)
    ov  = rga_IS[3, :]        # Observation value
    fv  = rga_IS[4, :]        # Model equivalent value
    av  = rga_IS[5, :]        # Analysis value (not used for now)
    dv  = rga_IS[6, :]        # Misfit value
    oe  = rga_IS[7, :]        # Observation error 
    #
    duid  = iga_IS[0, :]      # Track number
    Tstp  = iga_IS[1, :]      # Model time step corresonding to observation time
    setid = iga_IS[8, :]      # Instrument indicator (ALTIKA: 13; CRYOSAT2: 11; JASON2: 3; JASON3: 15; JASON2N: 16; HY2A: 14; SENTINEL3A: 17)
    qc    = iga_IS[9, :]      # QC values (O: good obs;  1: bad obs) 

    index = range(len(lon))
    df_IS        = pd.DataFrame(lon, index=index, columns=['Lon'])
    df_IS['Lat'] = pd.DataFrame(lat, index=index)
    df_IS['tt']  = pd.DataFrame(tt,  index=index)
    df_IS['obs']  = pd.DataFrame(ov,  index=index)
    df_IS['mod']  = pd.DataFrame(fv,  index=index)
    df_IS['ana']  = pd.DataFrame(av,  index=index)
    df_IS['misfit']  = pd.DataFrame(dv,  index=index)
    df_IS['oerr']  = pd.DataFrame(oe,  index=index)
    df_IS['TrackNum']  = pd.DataFrame(duid,  index=index)
    df_IS['Tstp']  = pd.DataFrame(Tstp,  index=index)
    df_IS['setID']  = pd.DataFrame(setid,  index=index)
    df_IS['QC']  = pd.DataFrame(qc,  index=index)
    # Convert tt to date
    df_IS['obsdate'] = num2date(tt, "days since 1950-01-01 00:00:00") 
    # Extract data by obs category
    df_IS_AL   = df_IS[df_IS['setID'] == 13]
    df_IS_C2   = df_IS[df_IS['setID'] == 11]
    df_IS_J2   = df_IS[df_IS['setID'] ==  3]
    df_IS_J3   = df_IS[df_IS['setID'] == 15]
    df_IS_J2N  = df_IS[df_IS['setID'] == 16]
    df_IS_H2   = df_IS[df_IS['setID'] == 14]
    df_IS_S3A  = df_IS[df_IS['setID'] == 17]

    print 'df_IS_AL accepted data number: ', len(df_IS_AL)
    print 'df_IS_AL rejected data number: ', len(df_IS_AL[df_IS_AL['QC'] == 1])
    print 'df_IS_C2 accepted data number: ', len(df_IS_C2)
    print 'df_IS_C2 rejected data number: ', len(df_IS_C2[df_IS_C2['QC'] == 1])

    print 'df_IS_J2 accepted data number: ', len(df_IS_J2)
    print 'df_IS_J2 rejected data number: ', len(df_IS_J2[df_IS_J2['QC'] == 1])

    print 'df_IS_J3 accepted data number: ', len(df_IS_J3)
    print 'df_IS_J3 rejected data number: ', len(df_IS_J3[df_IS_J3['QC'] == 1])

    print 'df_IS_J2N accepted data number: ', len(df_IS_J2N)
    print 'df_IS_J2N rejected data number: ', len(df_IS_J2N[df_IS_J2N['QC'] == 1])

    print 'df_IS_H2 accepted data number: ', len(df_IS_H2)
    print 'df_IS_H2 rejected data number: ', len(df_IS_H2[df_IS_H2['QC'] == 1])

    print 'df_IS_S3A accepted data number: ', len(df_IS_S3A)
    print 'df_IS_S3A rejected data number: ', len(df_IS_S3A[df_IS_S3A['QC'] == 1])
    
    # keep only accepted obs
    for df in df_IS_AL, df_IS_C2, df_IS_J2, df_IS_J3, df_IS_J2N, df_IS_H2, df_IS_S3A:
        df = df[df['QC'] == 0] 

    # Concatenate all obs families
    df_IS_ALL = pd.concat([df_IS_AL, df_IS_C2, df_IS_J2, df_IS_J3, df_IS_J2N, df_IS_H2, df_IS_S3A], axis=0, ignore_index=True)
    
    # Combine dataframes
    if len(df_IS_AL) > 0:
        df_AL = df_combine(df_IS_AL)
    else:
        df_AL = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_C2) > 0:
        df_C2 = df_combine(df_IS_C2)
    else:
        df_C2 = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_J2) > 0:
        df_J2 = df_combine(df_IS_J2)
    else:
        df_J2 = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_J3) > 0:
        df_J3 = df_combine(df_IS_J3)
    else:
        df_J3 = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_J2N) > 0:
        df_J2N = df_combine(df_IS_J2N)
    else:
        df_J2N = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_H2) > 0:
        df_H2 = df_combine(df_IS_H2)
    else:
        df_H2 = pd.DataFrame(np.nan, index=[], columns=[])

    if len(df_IS_S3A) > 0:
        df_S3A = df_combine(df_IS_S3A)
    else:
        df_S3A = pd.DataFrame(np.nan, index=[], columns=[])
    
    if len(df_IS_ALL) > 0:
        df_ALL = df_combine(df_IS_ALL)
    else:
        df_ALL = pd.DataFrame(np.nan, index=[], columns=[])

    df_AL_list.append(df_AL)
    df_C2_list.append(df_C2)
    df_J2_list.append(df_J2)
    df_J3_list.append(df_J3)
    df_J2N_list.append(df_J2N)
    df_H2_list.append(df_H2)
    df_S3A_list.append(df_S3A)
    df_ALL_list.append(df_ALL)

print 'begin concat'
df_AL_global = pd.concat(df_AL_list, axis=0, ignore_index=True, copy=False)
df_C2_global = pd.concat(df_C2_list, axis=0, ignore_index=True, copy=False)
df_J2_global = pd.concat(df_J2_list, axis=0, ignore_index=True, copy=False)
df_J3_global = pd.concat(df_J3_list, axis=0, ignore_index=True, copy=False)
df_J2N_global = pd.concat(df_J2N_list, axis=0, ignore_index=True, copy=False)
df_H2_global = pd.concat(df_H2_list, axis=0, ignore_index=True, copy=False)
df_S3A_global = pd.concat(df_S3A_list, axis=0, ignore_index=True, copy=False)
df_ALL_global = pd.concat(df_ALL_list, axis=0, ignore_index=True, copy=False)
   
print 'end concat'

# Combine global dataframes
#Altika
if len(df_AL_global) > 0:
    df_AL_global_cmd = combine_global(df_AL_global)
else:
    df_AL_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#Cryosat2
if len(df_C2_global) > 0:
    df_C2_global_cmd = combine_global(df_C2_global)
else:
    df_C2_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#Jason2
if len(df_J2_global) > 0:
    df_J2_global_cmd = combine_global(df_J2_global)
else:
    df_J2_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#Jason3
if len(df_J3_global) > 0:
    df_J3_global_cmd = combine_global(df_J3_global)
else:
    df_J3_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#Jason2N
if len(df_J2N_global) > 0:
    df_J2N_global_cmd = combine_global(df_J2N_global)
else:
    df_J2N_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#H2Y
if len(df_H2_global) > 0:
    df_H2_global_cmd = combine_global(df_H2_global)
else:
    df_H2_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#Sentinel
if len(df_S3A_global) > 0:
    df_S3A_global_cmd = combine_global(df_S3A_global)
else:
    df_S3A_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])

#All data
if len(df_ALL_global) > 0:
    df_ALL_global_cmd = combine_global(df_ALL_global)
else:
    df_ALL_global_cmd = pd.DataFrame(np.nan, index=[], columns=[])


# Treat the case of lon=-180 
if len(df_AL_global_cmd) > 0:
    df_AL_global_cmd_2 = transform_180(df_AL_global_cmd)
else:
    df_AL_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])

if len(df_C2_global_cmd) > 0:
    df_C2_global_cmd_2 = transform_180(df_C2_global_cmd)
else:
    df_C2_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_J2_global_cmd) > 0:
    df_J2_global_cmd_2 = transform_180(df_J2_global_cmd)
else:
    df_J2_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_J3_global_cmd) > 0:
    df_J3_global_cmd_2 = transform_180(df_J3_global_cmd)
else:
    df_J3_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_J2N_global_cmd) > 0:
    df_J2N_global_cmd_2 = transform_180(df_J2N_global_cmd)
else:
    df_J2N_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_H2_global_cmd) > 0:
    df_H2_global_cmd_2 = transform_180(df_H2_global_cmd)
else:
    df_H2_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_S3A_global_cmd) > 0:
    df_S3A_global_cmd_2 = transform_180(df_S3A_global_cmd)
else:
    df_S3A_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])
if len(df_ALL_global_cmd) > 0:
    df_ALL_global_cmd_2 = transform_180(df_ALL_global_cmd)
else:
    df_ALL_global_cmd_2 = pd.DataFrame(np.nan, index=[], columns=[])

# Save dataframes to pickle objects
pickle.dump(df_AL_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_AL.pkl", "wb" ) )
pickle.dump(df_C2_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_C2.pkl", "wb" ) )
pickle.dump(df_J2_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_J2.pkl", "wb" ) )
pickle.dump(df_J3_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_J3.pkl", "wb" ) )
pickle.dump(df_J2N_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_J2N.pkl", "wb" ) )
pickle.dump(df_H2_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_H2.pkl", "wb" ) )
pickle.dump(df_S3A_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_S3A.pkl", "wb" ) )
pickle.dump(df_ALL_global_cmd_2 , open( output_path + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_ALLSAT.pkl", "wb" ) )


# Plot misfit
if len(df_ALL_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_ALL_global_cmd_2, 'ALL_SAT')
if len(df_AL_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_AL_global_cmd_2, 'ALTIKA')
if len(df_C2_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_C2_global_cmd_2, 'CRYOSAT2')
if len(df_J2_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_J2_global_cmd_2, 'JASON2')
if len(df_J3_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_J3_global_cmd_2, 'JASON3')
if len(df_J2N_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_J2N_global_cmd_2, 'JASON2N')
if len(df_H2_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_H2_global_cmd_2, 'HY2A')
if len(df_S3A_global_cmd_2) > 0:
    plot_SLA_misfit_map(df_S3A_global_cmd_2, 'SENTINEL3A')

# Plot misfit rms
if len(df_ALL_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_ALL_global_cmd_2, 'ALL_SAT')
if len(df_AL_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_AL_global_cmd_2, 'ALTIKA')
if len(df_C2_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_C2_global_cmd_2, 'CRYOSAT2')
if len(df_J2_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_J2_global_cmd_2, 'JASON2')
if len(df_J3_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_J3_global_cmd_2, 'JASON3')
if len(df_J2N_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_J2N_global_cmd_2, 'JASON2N')
if len(df_H2_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_H2_global_cmd_2, 'HY2A')
if len(df_S3A_global_cmd_2) > 0:
    plot_SLA_misfit_rms_map(df_S3A_global_cmd_2, 'SENTINEL3A')

# Plot obs number
if len(df_ALL_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_ALL_global_cmd_2, 'ALL_SAT')
if len(df_AL_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_AL_global_cmd_2, 'ALTIKA')
if len(df_C2_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_C2_global_cmd_2, 'CRYOSAT2')
if len(df_J2_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_J2_global_cmd_2, 'JASON2')
if len(df_J3_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_J3_global_cmd_2, 'JASON3')
if len(df_J2N_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_J2N_global_cmd_2, 'JASON2N')
if len(df_H2_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_H2_global_cmd_2, 'HY2A')
if len(df_S3A_global_cmd_2) > 0:
    plot_SLA_obs_count_map(df_S3A_global_cmd_2, 'SENTINEL3A')

print 'Finished in : ', time.time()-start, ' s'

