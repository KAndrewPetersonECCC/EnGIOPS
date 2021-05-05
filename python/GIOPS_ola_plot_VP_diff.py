'''
Script purpose:

Produce graphics for msifit [O-P] rms difference between experiment and a reference
Read pkl files and produce rms difference figures for temperature and salinity  for depth ranges
([0-5m], [0-50m], [0-500m] and [500-2000m])
'''

import argparse
import os
import sys
import getopt
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
import cPickle as pickle
import matplotlib.colors as colors


class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))



def plot_VP_misfit_diff_map(df_s, df_r, dep, var):
    '''
    Purpose: plot VP misfit map
    Arguments:
    df_s: dataframe containing experiment data
    df_r: dataframe containing reference experiment data
    depth range:
    5:   0-5m
    10:  0-10m
    50:  0-50m
    500: 0-500m
    2000:500-2000m

    var: 'temperature' or 'salinity'
    '''
    df_s['lon_int'][df_s['lon_int'] < 0] += 360                
    df_r['lon_int'][df_r['lon_int'] < 0] += 360                
    
    # Merge the two dataframes
    df = pd.merge(df_s, df_r, on=['lat_int', 'lon_int'], how='inner')
 
    print (dep, var[0].upper()+var[1:].lower())
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=180, resolution='c')
    x, y = m(df['lon_int'].values, df['lat_int'].values)
    fig = plt.figure(figsize=(10, 6)) 
    if dep == 500:
        if var.lower() == 'temperature':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Temperature misfit rms difference in deg [0-500m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        elif var.lower() == 'salinity':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Salinity misfit rms difference in PSU [0-500m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 50:
        if var.lower() == 'temperature':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Temperature misfit rms difference in deg [0-50m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        elif var.lower() == 'salinity':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Salinity misfit rms difference in PSU [0-50m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 2000:
        if var.lower() == 'temperature':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Temperature misfit rms difference in deg [500-2000m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        elif var.lower() == 'salinity':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Salinity misfit rms difference in PSU [500-2000m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 10:
        if var.lower() == 'temperature':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Temperature misfit rms difference in deg [0-10m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        elif var.lower() == 'salinity':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Salinity misfit rms difference in PSU [0-10m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        else:
            sys.exit('plot_VP_misfit_map:  Something wrong with var argument ..')
    elif dep == 5:
        if var.lower() == 'temperature':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Temperature misfit rms difference in deg [0-5m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
        elif var.lower() == 'salinity':
            plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : Salinity misfit rms difference in PSU [0-5m]', fontsize=16, ha='center')
            plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
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
        vmin, vmax = -0.5, 0.5
        
    if var.lower() == 'salinity':
        vmin, vmax = -0.2, 0.2
    
    if var.lower() == 'temperature':
        clevs = np.linspace(-0.5, 0.5, 100)
        ticks = [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] 
    
    if var.lower() == 'salinity':
        clevs = np.linspace(-0.2, 0.2, 100)
        ticks = [-0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.1, 0.15, 0.20]
 
    norm = MidpointNormalize(vmin = vmin, vmax = vmax, midpoint=0, clip = False)
    
    colors = df['new_rms_y'].values - df['new_rms_x'].values
    cmap   = cm.get_cmap("bwr", len(clevs))
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, norm=norm, ax=ax)

    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    cb = plt.colorbar(im, cax=cax, orientation='horizontal', ticks=ticks)

    plt.savefig(output_path +'/INSITU_' + sdate + '_' + fdate + '_' + var.upper() + '_RMS_DIFF_map_'+ str(dep) + '.png')
    plt.clf()



# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",          required=True, help="Experiment name")
ap.add_argument("--ref_suite",      required=True, help="Reference experiment name")
ap.add_argument("--input_dir",      required=True, help="Input directory for experiment")
ap.add_argument("--ref_input_dir",  required=True, help="Input directory for experiment")
ap.add_argument("--output_dir",     required=True, help="Analysis date")
ap.add_argument("--start_date",     required=True, help="Start date")
ap.add_argument("--final_date",     required=True, help="Final date")


suite_name      = ap.parse_args().suite
ref_suite_name  = ap.parse_args().ref_suite
input_dir       = ap.parse_args().input_dir
ref_input_dir   = ap.parse_args().ref_input_dir
output_path     = ap.parse_args().output_dir
sdate           = ap.parse_args().start_date
fdate           = ap.parse_args().final_date

start_date = datetime.datetime.strptime(sdate, "%Y%m%d")
final_date = datetime.datetime.strptime(fdate, "%Y%m%d")


# Make sure dates are in order
if start_date > final_date:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)


# Print entered arguments
print 'Experiment name: ', suite_name
print 'Reference experiment name: ', suite_name
print 'Start date: ', sdate
print 'End date:   ', fdate


# Create output folder
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not ref_input_dir.endswith('/'):
    ref_input_dir = ref_input_dir + '/'
if not output_path.endswith('/'):
    output_path = output_path + '/'


# Retrieve dataframes from pickle objects
# Experiment
# Temperature
with open(input_dir + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_VP_T.pkl", 'rb') as fT:
    Ts_data_5        = pickle.load(fT)
    Ts_data_10       = pickle.load(fT)
    Ts_data_50       = pickle.load(fT)
    Ts_data_500      = pickle.load(fT)
    Ts_data_500_2000 = pickle.load(fT)
fT.close
# Salinity
with open(input_dir + "/save_" + suite_name + "_" + sdate + "_" + fdate + "_VP_S.pkl", 'rb') as fS:
    Ss_data_5        = pickle.load(fS)
    Ss_data_10       = pickle.load(fS)
    Ss_data_50       = pickle.load(fS)
    Ss_data_500      = pickle.load(fS)
    Ss_data_500_2000 = pickle.load(fS)
fS.close

# Reference experiment
# Temperature
with open(ref_input_dir + "/save_" + ref_suite_name + "_" + sdate + "_" + fdate + "_VP_T.pkl", 'rb') as fT:
    Tr_data_5        = pickle.load(fT)
    Tr_data_10       = pickle.load(fT)
    Tr_data_50       = pickle.load(fT)
    Tr_data_500      = pickle.load(fT)
    Tr_data_500_2000 = pickle.load(fT)
fT.close
# Salinity
with open(ref_input_dir + "/save_" + ref_suite_name + "_" + sdate + "_" + fdate + "_VP_S.pkl", 'rb') as fS:
    Sr_data_5        = pickle.load(fS)
    Sr_data_10       = pickle.load(fS)
    Sr_data_50       = pickle.load(fS)
    Sr_data_500      = pickle.load(fS)
    Sr_data_500_2000 = pickle.load(fS)
fS.close()

# Producing plots
#Temperature
plot_VP_misfit_diff_map(Ts_data_5, Tr_data_5, 5, 'temperature')
plot_VP_misfit_diff_map(Ts_data_10, Tr_data_10, 10, 'temperature')
plot_VP_misfit_diff_map(Ts_data_50, Tr_data_50, 50, 'temperature')
plot_VP_misfit_diff_map(Ts_data_500, Tr_data_500, 500, 'temperature')
plot_VP_misfit_diff_map(Ts_data_500_2000, Tr_data_500_2000, 2000, 'temperature')

#Salinity
plot_VP_misfit_diff_map(Ss_data_5, Sr_data_5, 5, 'salinity')
plot_VP_misfit_diff_map(Ss_data_10, Sr_data_10, 10, 'salinity')
plot_VP_misfit_diff_map(Ss_data_50, Sr_data_50, 50, 'salinity')
plot_VP_misfit_diff_map(Ss_data_500, Sr_data_500, 500, 'salinity')
plot_VP_misfit_diff_map(Ss_data_500_2000, Sr_data_500_2000, 2000, 'salinity')

