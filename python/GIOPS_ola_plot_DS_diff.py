'''
Script purpose:
Read and produce graphics for DS (SST) data.
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



def plot_SST_misfit_rms_difference_map(df1, df2, typ):
    
    '''
    Purpose: plot SST misfit RMS map
    Arguments:
    df1: dataframe 1 containing data
    df2: dataframe 2 containing data
    '''
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90, llcrnrlon=0,urcrnrlon=360, lon_0=180, resolution='c')
    df1['lon_int'][df1['lon_int'] < 0] += 360
    x, y = m( df1['lon_int'].values, df1['lat_int'].values)
    fig = plt.figure(figsize=(10, 6))
    #plt.rc('text', usetex=True)
    #plt.title(r"\begin{center} {\Large Temperature} \par {\large Humidity} \end{center}")
    if typ == 'SST':
        plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : SST misfit difference in deg', fontsize=16, ha='center')
    elif typ == 'SST_NIGHT':
        plt.figtext(0.5, 0.95, suite_name + ' vs ' + ref_suite_name +' : SST_NIGHT misfit difference in deg', fontsize=16, ha='center')

    plt.figtext(0.5, 0.90, sdate + '-' + fdate, fontsize=14, ha='center')
    ax = fig.gca()
    m.drawcoastlines()
    m.fillcontinents(color='white', zorder=1)
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.), labels=[True, False, False, False])
    m.drawmeridians(np.arange(-180.,181.,45.), labels=[False, False, False, True])
    ax.set_xlabel('Longitude', fontsize=12, labelpad=20)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=30)

    vmin, vmax = -0.2, 0.2
    clevs = np.linspace(vmin, vmax, 100)
    norm = MidpointNormalize(vmin = vmin, vmax = vmax, midpoint=0, clip = False)
    colors = df2['new_rms'].values - df1['new_rms'].values
    cmap   = cm.get_cmap("bwr", len(clevs))
    im = m.scatter(x, y, 10, marker='s', c=colors, cmap=cmap, norm=norm, ax=ax)
    normalize = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize, orientation='horizontal', extend='both')
    #cb = plt.colorbar(im, cax=cax, orientation='horizontal')
    c.ax.annotate('better', xy=(0.86, 1.2), xycoords='axes fraction')
    c.ax.annotate('worse', xy=(0.05, 1.2), xycoords='axes fraction')

#    norm = matplotlib.colors.Normalize(vmin = -0.2, vmax = 0.2, clip = False)
#    colors = plt.cm.coolwarm(norm(df2['new_rms'].values - df1['new_rms'].values))
#    im = m.scatter(x, y, 10, marker='s', color=colors, cmap=plt.cm.coolwarm, ax=ax)
#    clevs = np.linspace(-0.2, 0.2, 100)
#    bnorm  = matplotlib.colors.BoundaryNorm(clevs, len(clevs) - 1)
#    cmap   = cm.get_cmap("coolwarm", len(clevs) - 1)
#    ticks = [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]
#    cax, kw = matplotlib.colorbar.make_axes(ax, location='bottom', pad=0.15, shrink=0.8, fraction=0.05)
#    c = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=bnorm, ticks=ticks, orientation='horizontal', extend='both')
#    c.ax.tick_params(labelsize=12)
#    plt.show()
    if typ == 'SST':
        plt.savefig(output_dir +'/GEN_SST_' + sdate + '_' + fdate + '_RMS_DIFF_map.png')
    elif typ == 'SST_NIGHT':
        plt.savefig(output_dir +'/GEN_SST_NIGHT_' + sdate + '_' + fdate + '_RMS_DIFF_map.png')


# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",           required=True, help="Experiment name")
ap.add_argument("--ref_suite",       required=True, help="Reference experiment name")
ap.add_argument("--input_dir",       required=True, help="Experiment path")
ap.add_argument("--ref_input_dir",   required=True, help="Reference experiment path")
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

file_s = input_dir + 'save_' + suite_name + '_' + sdate + '_' + fdate + '_DS.pkl'
file_r = ref_input_dir + 'save_' + ref_suite_name + '_' + sdate + '_' + fdate + '_DS.pkl'

with open(file_s, 'rb') as fs:
    df_s_SST = pickle.load(fs)
    df_s_SST_NIGHT = pickle.load(fs)
with open(file_r, 'rb') as fr:
    df_r_SST = pickle.load(fr)
    df_r_SST_NIGHT = pickle.load(fr)
    
plot_SST_misfit_rms_difference_map(df_s_SST, df_r_SST, 'SST')
#plot_SST_misfit_rms_difference_map(df_s_SST_NIGHT, df_r_SST_NIGHT, 'SST_NIGHT')
