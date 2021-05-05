'''
Script purpose:
Read and produce graphics for IS (SLA) data.
Graphics are produced for mean difference in misfit [O-P] rms
'''

import struct
import argparse
import os, sys, getopt
import numpy as np
import pandas as pd
import datetime
from mpl_toolkits.basemap import Basemap
import warnings
import time
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import cm
from matplotlib.colors import ListedColormap
import  mimetypes
import cPickle as pickle
import matplotlib.colors as colors


warnings.filterwarnings('ignore')

start = time.time()

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def plot_IS_misfit_rms_difference_map(df1, df2, inst):
    
    '''
    Purpose: plot SLA misfit RMS difference map
    Arguments:
    df1: dataframe 1 containing data
    df2: dataframe 2 containing data
    inst: string defining the instrument (satellite) used
          ALL (all satellites), 'ALTIKA', 'CRYOSAT2', 'JASON2', 'JASON3', 'JASON2N', 'HY2A', 'SENTINEL3A'
    '''
    print 'Producing figure for ' + inst 
    
    df1['lon_int'][df1['lon_int'] < 0] += 360                
    df2['lon_int'][df2['lon_int'] < 0] += 360                
    
    # Merge the two dataframes
    df = pd.merge(df1, df2, on=['lat_int', 'lon_int'], how='inner')
    
    #m = Basemap(projection='npstere',boundinglat=40,lon_0=340,resolution='l')
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    x, y = m( df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)); ax = fig.gca() 
    #fig = plt.figure(figsize=(8, 8)) 
    plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : '+inst+ ' misfit rms difference in cm', fontsize=16, ha='center')
    plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)

    vmin, vmax = -2.0, 2.0
    clevs = np.linspace(vmin, vmax, 100)
    norm = MidpointNormalize(vmin = vmin, vmax = vmax, midpoint=0, clip = False)
    colors = df['new_rms_y'].values - df['new_rms_x'].values
    cmap   = cm.get_cmap("bwr", len(clevs))
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, norm=norm, ax=ax)

    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    cb = plt.colorbar(im, cax=cax, orientation='horizontal')



#    norm = matplotlib.colors.Normalize(vmin = -2.0, vmax = 2.0, clip = False)
    #colors = plt.cm.coolwarm(norm(df['new_rms_y'].values - df['new_rms_x'].values))
#    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
#    clevs = np.arange(-2.0, 2.1, 0.1)
#    ticks = np.arange(-2.0, 2.1, 0.5)
#    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
#    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
#    cmap.set_bad(color='black')
#    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
#    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
#    c.ax.tick_params(labelsize=12)

    plt.savefig(output_dir + inst + '_' + sdate + '_' + fdate + '_RMS_DIFF_map.png')


# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",           required=True, help="Experiment name")
ap.add_argument("--ref_suite",       required=True, help="Reference experiment name")
ap.add_argument("--input_dir",       required=True, help="Experiment path")
ap.add_argument("--ref_input_dir",   required=True, help="Experiment path")
ap.add_argument("--output_dir",      required=True, help="Output path")
ap.add_argument("--start_date",      required=True, help="Start date")
ap.add_argument("--final_date",      required=True, help="Final date")

suite_name       = ap.parse_args().suite
ref_suite_name   = ap.parse_args().ref_suite
input_dir        = ap.parse_args().input_dir
ref_input_dir    = ap.parse_args().ref_input_dir
output_dir       = ap.parse_args().output_dir
sdate            = ap.parse_args().start_date
fdate            = ap.parse_args().final_date

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not ref_input_dir.endswith('/'):
    ref_input_dir = ref_input_dir + '/'
if not output_dir.endswith('/'):
    output_dir = output_dir + '/'


start_date = datetime.datetime.strptime(sdate, "%Y%m%d")
final_date = datetime.datetime.strptime(fdate, "%Y%m%d")


# Make sure dates are in order
if start_date > final_date:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)


# Print entered arguments
print 'Experiment name:           ', suite_name
print 'Reference experiment name: ', ref_suite_name
print 'Input path:                ', input_dir
print 'Ref input path:            ', ref_input_dir
print 'Start date:      ', sdate
print 'End date:        ', fdate


# Retrieve data from pickle
#AL
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_AL.pkl', 'rb') as fs:
    df_s_AL_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_AL.pkl', 'rb') as fs:
    df_r_AL_global = pickle.load(fs)

#C2
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_C2.pkl', 'rb') as fs:
    df_s_C2_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_C2.pkl', 'rb') as fs:
    df_r_C2_global = pickle.load(fs)

#J2
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_J2.pkl', 'rb') as fs:
    df_s_J2_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_J2.pkl', 'rb') as fs:
    df_r_J2_global = pickle.load(fs)

#J3
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_J3.pkl', 'rb') as fs:
    df_s_J3_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_J3.pkl', 'rb') as fs:
    df_r_J3_global = pickle.load(fs)

#J2N
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_J2N.pkl', 'rb') as fs:
    df_s_J2N_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_J2N.pkl', 'rb') as fs:
    df_r_J2N_global = pickle.load(fs)

#H2
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_H2.pkl', 'rb') as fs:
    df_s_H2_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_H2.pkl', 'rb') as fs:
    df_r_H2_global = pickle.load(fs)

#S3A
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_S3A.pkl', 'rb') as fs:
    df_s_S3A_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_S3A.pkl', 'rb') as fs:
    df_r_S3A_global = pickle.load(fs)

#ALL-SAT
with open(input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_ALLSAT.pkl', 'rb') as fs:
    df_s_ALLSAT_global = pickle.load(fs)
with open(ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_ALLSAT.pkl', 'rb') as fs:
    df_r_ALLSAT_global = pickle.load(fs)

# Produce figures
if not df_s_AL_global.empty and not df_r_AL_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_AL_global, df_r_AL_global, 'ALTIKA')

if not df_s_C2_global.empty and not df_r_C2_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_C2_global, df_r_C2_global, 'CRYOSAT2')

if not df_s_J2_global.empty and not df_r_J2_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_J2_global, df_r_J2_global, 'JASON2')

if not df_s_J3_global.empty and not df_r_J3_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_J3_global, df_r_J3_global, 'JASON3')
    
if not df_s_J2N_global.empty and not df_r_J2N_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_J2N_global, df_r_J2N_global, 'JASON2N')

if not df_s_H2_global.empty and not df_r_H2_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_H2_global, df_r_H2_global, 'HY2A')

if not df_s_S3A_global.empty and not df_r_S3A_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_S3A_global, df_r_S3A_global, 'SENTINEL3A')

if not df_s_ALLSAT_global.empty and not df_r_ALLSAT_global.empty:
    plot_IS_misfit_rms_difference_map(df_s_ALLSAT_global, df_r_ALLSAT_global, 'ALL_SAT')


