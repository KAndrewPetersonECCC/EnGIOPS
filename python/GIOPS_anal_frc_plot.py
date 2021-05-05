import matplotlib
matplotlib.use('Agg')

from netCDF4 import Dataset
import argparse
import os
import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.basemap import Basemap
from scipy.spatial import cKDTree
import pickle
import matplotlib.colors as colors
from matplotlib.pyplot import cm
import matplotlib as mpl
from mpl_toolkits.axes_grid1.colorbar import colorbar
from datetime import date, timedelta, datetime
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.mpl.ticker as cticker

import time
start_time0 = time.time()
start_time = time.time()

def s2date(nbdays):
    # enter nb of days since 1950 01 01    
    start = date(1950, 1, 1)      
    delta = timedelta(nbdays)     
    offset = start + delta   
    return offset

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def plot_map(vmin, vmax):
    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.coastlines(resolution='50m')
    ax.set_global()
    ax.add_feature(cartopy.feature.LAND, facecolor='grey')
    ax.add_feature(cartopy.feature.COASTLINE, linewidth=0.5)
    ax.add_feature(cartopy.feature.LAKES, alpha=0.3)
    ax.add_feature(cartopy.feature.RIVERS, linewidth=0.5)
    xlocs = [-135, -90, -45, 0, 45, 90, 135, 180]
    ylocs = [-90, -60, -30, 0, 30, 60, 90]
    ax.set_xticks(xlocs, crs=ccrs.PlateCarree())
    ax.set_xticklabels(xlocs, color='black', fontsize=8)
    ax.set_yticks(ylocs, crs=ccrs.PlateCarree())
    ax.set_yticklabels(ylocs, color='black', fontsize=8)
    ax.tick_params(axis='x', labeltop=True, labelbottom=True, pad=2.0, length=0.0)
    ax.tick_params(axis='y', labelleft=True, labelright=True, pad=2.0, length=0.0)
    lon_formatter = cticker.LongitudeFormatter()
    lat_formatter = cticker.LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.grid(linewidth=0.5, color='black', alpha=0.5, linestyle='dotted')
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18)
    return ax

def plot_sla():
    plt.clf()
    # Nearest interpolation
    inc = sla.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    # Cap values
    inc = np.ma.where(inc>1, 1, inc)
    inc = np.ma.where(inc<-1, -1, inc)
    norm = MidpointNormalize(vmin = -1.0, vmax = 1.0, midpoint=0, clip = False)
    clevs = np.linspace(-1.0, 1.1, 50)
    print (len(clevs))
    cmap = cm.get_cmap("seismic", len(clevs))
    ax = plot_map(vmin, vmax)
    #im = ax.contourf(xx, yy, inc, levels=clevs, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    im = ax.pcolormesh(xx, yy, inc, cmap=cmap, norm=norm, vmin=-1.0, vmax=1.0, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = [-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('meters', fontsize=9)
    cb.ax.set_xlim(-1.0, 1.0)
    title = 'Sea level anomaly  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_SLA_' + exp_date + '_'+suite+'.png')


def plot_mldp():
    # Mixing layer depth 
    plt.clf()
    # Nearest interpolation
    inc = hmld.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    clevs = np.concatenate((np.linspace(0, 100, 10), np.linspace(101, 1000, 30), np.linspace(1001, inc.max(), 10)), axis=0)
    print (len(clevs))
    cmap   = cm.get_cmap("viridis", len(clevs))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=clevs, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('Meters', fontsize=9)
    title = 'Mixing layer depth  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_MLDP_' + exp_date + '_'+suite+'.png')

def plot_emp():
    # Fresh water flux
    plt.clf()
    # Nearest interpolation
    inc = emp.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Convert to mm/day
    inc = inc * 86400.
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    # Cap values
    inc = np.ma.where(inc>100, 100, inc)
    inc = np.ma.where(inc<-100, -100, inc)
    #plot
    norm = MidpointNormalize(vmin = -100.0, vmax = 100.0, midpoint=0, clip = False)
    clevs = np.linspace(-100.0, 100.0, 50)
    print (len(clevs))
    cmap   = cm.get_cmap("seismic", len(clevs))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=clevs, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = [-100, -80, -60, -40, -20, 0.0, 20, 40, 60, 80, 100]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('kg/m2/day', fontsize=9)
    cb.ax.set_xlim(-100.0, 100.0)
    title = 'Fresh water flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_EMP_' + exp_date + '_'+suite+'.png')

def plot_qh():
    ## Latent heat flux
    plt.clf()
    # Nearest interpolation
    inc = qh.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc>300, 300, inc)
    inc = np.ma.where(inc<-300, -300, inc)
    #plot
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    print (len(levels))
    cmap   = cm.get_cmap("seismic", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    title = 'Latent heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_QH_' + exp_date + '_'+suite+'.png')

def plot_qs():
    # Sensible heat flux
    plt.clf()
    # Nearest interpolation
    inc = qs.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    print (len(levels))
    cmap   = cm.get_cmap("seismic", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    title = 'Sensible heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_QS_' + exp_date + '_'+suite+'.png')

def plot_q():
    # Net downward heat flux
    plt.clf()
    # Nearest interpolation
    inc = q.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    print (len(levels))
    cmap   = cm.get_cmap("seismic", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    title = 'Net downward heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_Q_' + exp_date + '_'+suite+'.png')

def plot_qlw():
    # Infrared heat flux over the ocean
    plt.clf()
    # Nearest interpolation
    inc = qlw.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    print (len(levels))
    cmap   = cm.get_cmap("seismic", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    title = 'Infrared heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_QLW_' + exp_date + '_'+suite+'.png')

def plot_tau():
    # Wind stress
    plt.clf()
    # Nearest interpolation
    inc = tau.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    levels = np.arange(np.finfo(float).eps, inc.max(), 0.1)
    print (len(levels))
    cmap   = cm.get_cmap("viridis", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 3.1, 1)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 3)
    cb.ax.set_title('N/m2', fontsize=9)
    title = 'Wind stress magnitude on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_TAU_' + exp_date + '_'+suite+'.png')

def plot_qsr():
    # net solar flux at at the ocean surface
    plt.clf()
    # Nearest interpolation
    inc = qsr.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    levels = np.arange(np.finfo(float).eps, inc.max(), 20)
    print (len(levels))
    cmap   = cm.get_cmap("viridis", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 300)
    cb.ax.set_title('W/m2', fontsize=9)
    title = 'Net solar flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_QSR_' + exp_date + '_'+suite+'.png')

def plot_tair():
    # 2m air temperature
    plt.clf()
    # Nearest interpolation
    inc = tair.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    levels = np.arange(inc.min(), inc.max(), 1.0)
    print (len(levels))
    cmap   = cm.get_cmap("coolwarm", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-30, 30.1, 5)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(-30, 30)
    cb.ax.set_title('Deg C', fontsize=9)
    title = 'Air temperature at 2m on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_TAIR_' + exp_date + '_'+suite+'.png')

def plot_pr():
    # Surface rainfall flux
    plt.clf()
    # Nearest interpolation
    inc = pr.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    inc = inc * 86400. * 1000.
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    levels = np.arange(0, inc.max(), 0.05)
    print (len(levels))
    cmap   = cm.get_cmap("viridis", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 3.1, 1)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 3)
    cb.ax.set_title(r'$10^{-3}$' + ' kg/m2/day', fontsize=9)
    title = 'Surface rainfall flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_PR_' + exp_date + '_'+suite+'.png')

def plot_w():
    # Surface verical velocity
    plt.clf()
    # Nearest interpolation
    inc = w.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3e' %inc.min()
    vmax = '%.3e' %inc.max()
    inc = inc * 10e5
    inc = np.ma.where(inc<-1, -1, inc)
    inc = np.ma.where(inc>1, 1, inc)
    #plot
    norm = MidpointNormalize(vmin = -1., vmax = 1., midpoint=0, clip = False)
    levels = np.arange(-1, 1.1, 0.05)
    print (len(levels))
    cmap   = cm.get_cmap("seismic", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-1, 1.1, 0.2)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title(r'$10^{-5}$' + 'm/s', fontsize=9)
    xs = min(1, inc.max())
    xn = max(-1, inc.min())
    cb.ax.set_xlim(xn, xs)
    title = 'Surface vertical velocity  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_W_' + exp_date + '_'+suite+'.png')

def plot_u10m():
    # Wind magnitude at 10m
    plt.clf()
    # Nearest interpolation
    inc = u10m.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = np.ma.masked_where(lat2d < -77, inc)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    levels = np.arange(np.finfo(float).eps, inc.max(), 0.5)
    print (len(levels))
    cmap   = cm.get_cmap("viridis", len(levels))
    ax = plot_map(vmin, vmax)
    im = ax.contourf(xx, yy, inc, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 20.1, 5)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 20)
    cb.ax.set_title('m/s', fontsize=9)
    title = '10 m wind magnitude on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_anal_U10M_' + exp_date + '_'+suite+'.png')

# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",    required=True, help="Experiment ID")
ap.add_argument("--expindir", required=True, help="Input directory for experiment")
ap.add_argument("--exp_date", required=True, help="Analysis date")
ap.add_argument("--outdir",   required=True, help="Output directory for experiment")
ap.add_argument("--figsize",  required=True, help="Figure size")


suite      = ap.parse_args().suite
indir      = ap.parse_args().expindir
exp_date   = ap.parse_args().exp_date
outdir     = ap.parse_args().outdir
fig_size   = ap.parse_args().figsize
fig_width  = float(fig_size.split('x')[0])
fig_height = float(fig_size.split('x')[1])


print ('Suite             = ', suite)
print ('Date              = ', exp_date)
print ('Input path        = ', indir)
print ('Output path       = ', outdir)



# Dates definition
date_m0 = datetime.strptime(exp_date, "%Y%m%d")
date_m1 = date_m0 - timedelta(days=1)
date_p5 = date_m0 + timedelta(days=5)

str_date_title = datetime.strftime(date_m0, "%Y-%m-%d")
str_date_m1    = datetime.strftime(date_m1, "%Y%m%d")
str_date_p5    = datetime.strftime(date_p5, "%Y%m%d")

# Make sure paths end with /
if not indir.endswith('/'):
    indir = indir + '/'
if not outdir.endswith('/'):
    outdir = outdir + '/'

# Filenames prefixes
prefixdAT = 'ORCA025-CMC-ANAL_1d_gridT-RUN-crs_' 
prefixdAU = 'ORCA025-CMC-ANAL_1d_gridU-RUN-crs_' 
prefixdAV = 'ORCA025-CMC-ANAL_1d_gridV-RUN-crs_' 

# Input file 1
if os.path.isfile(indir + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc'):
    input_file1 = indir + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc'
elif os.path.isfile(indir + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc.gz'):
    os.system('gunzip ' + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc.gz')
    input_file1 = indir + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc'
else:
    sys.exit('Input file does not exist:' + indir + prefixdAT + str_date_m1 + '-' + str_date_p5 + '.nc[.gz]')

# Input file 2
if os.path.isfile(indir + prefixdAU + str_date_m1 + '-' + str_date_p5 + '.nc'):
    input_file2 = indir + prefixdAU + str_date_m1 + '-' + str_date_p5 + '.nc'
elif os.path.isfile(indir + prefixdAU + str_date_m1 + '-' + str_date_p5 + '.nc.gz'):
    os.system('gunzip ' + prefixdAU  + str_date_m1 + '-' + str_date_p5 + '.nc.gz')
    input_file2 = indir + prefixdAU  + str_date_m1 + '-' + str_date_p5 + '.nc'
else:
    sys.exit('Input file does not exist:' + indir + prefixdAU + str_date_m1 + '-' + str_date_p5 + '.nc[.gz]')

# Input file 3
if os.path.isfile(indir + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc'):
    input_file3 = indir + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc'
elif os.path.isfile(indir + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc.gz'):
    os.system('gunzip ' + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc.gz')
    input_file3 = indir + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc'
else:
    sys.exit('Input file does not exist:' + indir + prefixdAV + str_date_m1 + '-' + str_date_p5 + '.nc[.gz]')

# Retrieve distances and indices for the target grid (regular lat/lon)
#d_inds = np.load('/home/kch001/my_src/GIOPS/constants/dist-indic-012.npy')
d_inds = np.load('/home/kch001/my_src/GIOPS/constants/dist-indic-012.npy')
d, inds = d_inds[0], d_inds[1]

# Read variables
f1 = Dataset(input_file1, mode='r')
f2 = Dataset(input_file2, mode='r')
f3 = Dataset(input_file3, mode='r')


lons = f1.variables['nav_lon'][:]              # longitudes
lats = f1.variables['nav_lat'][:]              # latitudes

sla     = f1.variables['SLA'][:].squeeze()     # sea level anomaly
sshn    = f1.variables['SSHN'][:].squeeze()    # sea level height
sst     = f1.variables['SST'][:].squeeze()     # sea surface temperature
hmld    = f1.variables['HMLD'][:].squeeze()    # mixed layer depth
w       = f1.variables['W'][:].squeeze()       # surface vertical velocity
emp     = f1.variables['EMP'][:].squeeze()     # fresh water flux
hbar    = f1.variables['HBAR'][:].squeeze()    # barotropic height
tssh    = f1.variables['T_SSH'][:].squeeze()   # temporal mean ssh
thbar1  = f1.variables['T_HBAR1'][:].squeeze() # mean barotropic height (cycle 1)
thbar2  = f1.variables['T_HBAR2'][:].squeeze() # mean barotropic height (cycle 2)
t_diffhbar  = f1.variables['T_DIFFHBAR'][:].squeeze() # HBAR1 and HBAR2 difference (smooth)
ssh_eq  = f1.variables['SSH_EQUIVALENT'][:].squeeze() # SSH model equivalent(mean ssh - diffhbar)
sla_eq  = f1.variables['SLA_EQUIVALENT'][:].squeeze() # Equivalent sea level anomaly (ssh - diffhbar - observed mssh)
pr      = f1.variables['P'][:].squeeze()       # Surface rainfall flux
u10m    = f1.variables['U10m'][:].squeeze()    # 10m wind speed
qs      = f1.variables['QS'][:].squeeze()      # sensible heat flux over ocean
qlw     = f1.variables['QLW'][:].squeeze()     # infrared heat flux over ocean
qh      = f1.variables['QH'][:].squeeze()      # latent heat flux over ocean
qsr     = f1.variables['QSR'][:].squeeze()     # net solar flux at at the ocean surface
q       = f1.variables['Q'][:].squeeze()       # net downward heat
tair    = f1.variables['TAIR'][:].squeeze()    # air temperature
h2m     = f1.variables['H2M'][:].squeeze()     # relative humidity
tinst   = f1.variables['TINST'][:].squeeze()   # instantaneous temperature
sinst   = f1.variables['SINST'][:].squeeze()   # instantaneous salinity
mssh    = f1.variables['MSSH'][:].squeeze()    # mean sea surface height
sst_day_mean = f1.variables['SSTMEANDAILY'][:].squeeze()    # daily mean sea surface temperature
sst_night_mean = f1.variables['SSTMEANNIGHT'][:].squeeze()    # night-time mean sea surface temperature
var_sst_day_mean = f1.variables['VAR_TN_SSTMEANDAILY'][:].squeeze()      # daily mean model sst minus observed sst
var_sst_night_mean = f1.variables['VAR_TN_SSTMEANNIGHT'][:].squeeze()    # night-time mean model sst minus observed sst

taux = f2.variables['TAUX'][:].squeeze() # wind stress x-component
tauy = f3.variables['TAUY'][:].squeeze() # wind stress y-component
tau  = np.sqrt(taux*taux + tauy*tauy)    # wind stress magnitude

lons = np.where(lons<0, lons+360, lons)

deltax=1.0/12
deltay=1.0/12

xx = np.arange(0, 360+deltax, deltax)
yy = np.arange(-90, 90+deltay, deltay)
lon2d, lat2d = np.meshgrid(xx, yy)



print('plotting sla ...'); plot_sla()
print('plotting mldp...'); plot_mldp()
print('plotting emp...'); plot_emp()
print('plotting qh...'); plot_qh()
print('plotting qs...'); plot_qs()
print('plotting q...'); plot_q()
print('plotting qlw...'); plot_qlw()
print('plotting tau...'); plot_tau()
print('plotting qsr...'); plot_qsr()
print('plotting tair...'); plot_tair()
print('plotting pr...'); plot_pr()
print('plotting w...'); plot_w()
print('plotting u10m...'); plot_u10m()
print('total: ', time.time() - start_time0)
