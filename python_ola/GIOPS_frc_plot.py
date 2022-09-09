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
import datetime
from mpl_toolkits.axes_grid1.colorbar import colorbar



class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def fig_init():
    m.fillcontinents(color='gray')
    m.drawmeridians(np.arange(0,405,45), labels=[True,True,True,True], color='k', linewidth=0.5, xoffset=1.6, yoffset=1.6, fontsize=8)
    m.drawparallels(np.arange(-90,120,30), labels=[True,True,True,True], color='k', linewidth=0.5, xoffset=0.6, yoffset=0.6, fontsize=8)

def plot_sla():
    # Nearest interpolation
    inc = sla.flatten()[inds.astype(int)].reshape(lon2d.shape)
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    # Cap values
    inc = np.ma.where(inc>1, 1, inc)
    inc = np.ma.where(inc<-1, -1, inc)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -1.0, vmax = 1.0, midpoint=0, clip = False)
    clevs = np.linspace(-1.0, 1.1, 100)
    levels_inc = np.arange(inc.min(), inc.max(), 0.05)
    cmap   = cm.get_cmap("seismic", len(clevs))
    im = m.contourf(x, y, inc, levels=clevs, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = [-1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('meters', fontsize=9)
    cb.ax.set_xlim(-1.0, 1.0)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Sea level anomaly  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_SLA_' + exp_date + '_'+suite+'.png')

def plot_mldp():
    # Mixing layer depth 
    plt.clf()
    # Nearest interpolation
    inc = hmld.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    clevs = np.concatenate((np.linspace(0, 100, 10), np.linspace(101, 1000, 100), np.linspace(1001, inc.max(), 100)), axis=0)
    cmap   = cm.get_cmap("jet", len(clevs))
    im = m.contourf(x, y, inc, levels=clevs, cmap=cmap, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('Meters', fontsize=9)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Mixing layer depth  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_MLDP_' + exp_date + '_'+suite+'.png')

def plot_emp():
    # Fresh water flux
    plt.clf()
    # Nearest interpolation
    inc = emp.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Convert to mm/day
    inc = inc * 86400.
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    # Cap values
    inc = np.ma.where(inc>100, 100, inc)
    inc = np.ma.where(inc<-100, -100, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -100.0, vmax = 100.0, midpoint=0, clip = False)
    clevs = np.linspace(-100.0, 100.0, 1000)
    cmap   = cm.get_cmap("seismic", len(clevs))
    im = m.contourf(x, y, inc, levels=clevs, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = [-100, -80, -60, -40, -20, 0.0, 20, 40, 60, 80, 100]
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('kg/m2/day', fontsize=9)
    cb.ax.set_xlim(-100.0, 100.0)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Fresh water flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_EMP_' + exp_date + '_'+suite+'.png')

def plot_qh():
    ## Latent heat flux
    plt.clf()
    # Nearest interpolation
    inc = qh.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc>300, 300, inc)
    inc = np.ma.where(inc<-300, -300, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    cmap   = cm.get_cmap("seismic", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    #cb.ax.set_xlim(-300, 300)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Latent heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_QH_' + exp_date + '_'+suite+'.png')

def plot_qs():
    # Sensible heat flux
    plt.clf()
    # Nearest interpolation
    inc = qs.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    cmap   = cm.get_cmap("seismic", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Sensible heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_QS_' + exp_date + '_'+suite+'.png')

def plot_q():
    # Net downward heat flux
    plt.clf()
    # Nearest interpolation
    inc = q.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    cmap   = cm.get_cmap("seismic", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Net downward heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_Q_' + exp_date + '_'+suite+'.png')

def plot_qlw():
    # Infrared heat flux over the ocean
    plt.clf()
    # Nearest interpolation
    inc = qlw.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-300, -300, inc)
    inc = np.ma.where(inc>300, 300, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -300., vmax = 300., midpoint=0, clip = False)
    levels = np.arange(-300, 301, 10)
    cmap   = cm.get_cmap("seismic", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-300, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title('W/m2', fontsize=9)
    xs = min(300, inc.max())
    xn = max(-300, inc.min())
    cb.ax.set_xlim(xn, xs)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Infrared heat flux  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_QLW_' + exp_date + '_'+suite+'.png')

def plot_tau():
    # Wind stress
    plt.clf()
    # Nearest interpolation
    inc = tau.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    levels = np.arange(np.finfo(float).eps, inc.max(), 0.1)
    cmap   = cm.get_cmap("jet", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 3.1, 1)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 3)
    cb.ax.set_title('N/m2', fontsize=9)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Wind stress magnitude on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_TAU_' + exp_date + '_'+suite+'.png')

def plot_qsr():
    # net solar flux at at the ocean surface
    plt.clf()
    # Nearest interpolation
    inc = qsr.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    levels = np.arange(np.finfo(float).eps, inc.max(), 1)
    cmap   = cm.get_cmap("jet", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 301, 50)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 300)
    cb.ax.set_title('W/m2', fontsize=9)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Net solar flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_QSR_' + exp_date + '_'+suite+'.png')

def plot_tair():
    # 2m air temperature
    plt.clf()
    # Nearest interpolation
    inc = tair.flatten()[inds.astype(int)].reshape(lon2d.shape)
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    levels = np.arange(inc.min(), inc.max(), 0.1)
    cmap   = cm.get_cmap("jet", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-30, 30.1, 5)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(-30, 30)
    cb.ax.set_title('Deg C', fontsize=9)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Air temperature at 2m on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_TAIR_' + exp_date + '_'+suite+'.png')

def plot_pr():
    # Surface rainfall flux
    plt.clf()
    # Nearest interpolation
    inc = pr.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = inc * 86400. * 1000.
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    levels = np.arange(0, inc.max(), 0.05)
    cmap   = cm.get_cmap("jet", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(0, 3.1, 1)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_xlim(0, 3)
    cb.ax.set_title(r'$10^{-3}$' + ' kg/m2/day', fontsize=9)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Surface rainfall flux on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_PR_' + exp_date + '_'+suite+'.png')

def plot_w():
    # Surface verical velocity
    plt.clf()
    # Nearest interpolation
    inc = w.flatten()[inds.astype(int)].reshape(lon2d.shape)
    inc = inc * 10e5
    # Extremes values
    vmin = '%.3f' %inc.min()
    vmax = '%.3f' %inc.max()
    inc = np.ma.where(inc<-1, -1, inc)
    inc = np.ma.where(inc>1, 1, inc)
    #plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_init()
    norm = MidpointNormalize(vmin = -1., vmax = 1., midpoint=0, clip = False)
    levels = np.arange(-1, 1.1, 0.05)
    cmap   = cm.get_cmap("seismic", len(levels))
    im = m.contourf(x, y, inc, levels=levels, cmap=cmap, norm=norm, ax=ax)
    axin = inset_axes(ax,width="60%",height="3%",loc='lower center',bbox_to_anchor=(0,-0.2,1,1),bbox_transform=ax.transAxes,borderpad=0.5)
    ticks  = np.arange(-1, 1.1, 0.2)
    cb = colorbar(im, cax=axin, orientation="horizontal", ticks=ticks)
    cb.ax.set_title(r'$10^{-5}$' + 'm/s', fontsize=9)
    xs = min(1, inc.max())
    xn = max(-1, inc.min())
    cb.ax.set_xlim(xn, xs)
    ax.text(0.25, -0.13, 'Min= ' + vmin, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.75, -0.13, 'Max= ' + vmax, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=8)
    ax.text(0.02, 1.1, suite, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=18) 
    title = 'Surface vertical velocity  on ' + str_date_title +'\n'
    ax.set_title(title, fontsize=18, loc='center')
    plt.savefig(outdir +'crs_W_' + exp_date + '_'+suite+'.png')

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



# Dates manipulation
date_m0 = datetime.datetime.strptime(exp_date, "%Y%m%d")
date_m1 = date_m0 - datetime.timedelta(days=1)
date_p5 = date_m0 + datetime.timedelta(days=5)

str_date_title = datetime.datetime.strftime(date_m0, "%Y-%m-%d")
str_date_m1    = datetime.datetime.strftime(date_m1, "%Y%m%d")
str_date_p5    = datetime.datetime.strftime(date_p5, "%Y%m%d")

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


# Plots production
m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=0, urcrnrlon=360, lon_0=180, resolution='l')
x, y = m(lon2d, lat2d)

print('plotting sla ...'); plot_sla()
#print('plotting mldp...'); plot_mldp()
#print('plotting emp...'); plot_emp()
#print('plotting qh...'); plot_qh()
#print('plotting qs...'); plot_qs()
#print('plotting q...'); plot_q()
#print('plotting qlw...'); plot_qlw()
#print('plotting tau...'); plot_tau()
#print('plotting qsr...'); plot_qsr()
#print('plotting tair...'); plot_tair()
#print('plotting pr...'); plot_pr()
print('plotting w...'); plot_w()




