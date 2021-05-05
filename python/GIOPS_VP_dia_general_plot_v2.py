#! /usr/bin/env python
'''
Author: Kamel Chikhar 2018/04/18
General script that reads dia profile data and produce temporal and temporal means plots
'''

# Import needed modules
import argparse
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, MaxNLocator
from matplotlib.dates import date2num, num2date, DateFormatter, DateLocator, MonthLocator, WeekdayLocator, WEDNESDAY
from matplotlib import cm
import sys, os, errno, getopt
import time
import pickle

initial_time = time.time()


# Define functions
def read_file(path, suite, date, obs):
    '''
    function to read sst statistic data from SAM/DIA file
    Input:
    analysis date
    suite name
    suite path
    obs name
    Output: Numpy array containing the statistics
    '''
    infile = path + '/' + date + '/DIA/' + date + '00_SAM.dia_' + obs
    if os.path.isfile(infile):
        return pd.read_csv(infile, skiprows=2, delim_whitespace=True, na_values=['-0.17977+309'], usecols=(2, 3, 4, 6, 8))
    elif os.path.isfile(infile + '.gz'):
        return pd.read_csv(infile + '.gz', compression='gzip', skiprows=2, delim_whitespace=True, na_values=['-0.17977+309'], usecols=(2, 3, 4, 6, 8))
    else:
        sys.exit(infile + " does not exist")


def plot_setup_2000(ax):
    '''
    setup plot general features
    '''
    ax.set_ylim([-2000, 0])
    ax.set_yticks([0, -500, -1000, -1500, -2000])
    ax.yaxis.set_major_locator(MultipleLocator(500))
    ax.yaxis.set_minor_locator(MultipleLocator(100))
    ax.tick_params('y', length=10, width=1.2, which='major', direction='in')
    ax.tick_params('x', length=0, width=0, which='major', direction='in')
    ax.tick_params('both', length=5, width=1, which='minor', direction='in')
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_ylabel('Depth', fontsize=14)
    return ()

def plot_setup_200(ax):
    '''
    setup plot general features
    '''
    ax.set_ylim([-200, 0])
    ax.set_yticks([0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -120, -140, -160, -180, -200])
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params('y', length=10, width=1.2, which='major', direction='in')
    ax.tick_params('x', length=0, width=0, which='major', direction='in')
    ax.tick_params('both', length=5, width=1, which='minor', direction='in')
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_ticks_position('bottom')
    ax.set_ylabel('Depth', fontsize=14)
    return ()

def mean_plot_setup_2000(ax):
    '''
    setup plot general features
    '''
    ax.set_ylim([-2000, 0])
    ax.set_yticks([0, -500, -1000, -1500, -2000])
    ax.yaxis.set_major_locator(MultipleLocator(500))
    ax.yaxis.set_minor_locator(MultipleLocator(100))
    ax.tick_params('both', length=10, width=1.2, which='major', direction='in')
    ax.tick_params('both', length=5, width=1, which='minor', direction='in')
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    ax.set_ylabel('Depth(m)', fontsize=14)

def mean_plot_setup_200(ax):
    '''
    setup plot general features
    '''
    ax.set_ylim([-200, 0])
    ax.set_yticks([0, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -120, -140, -160, -180, -200])
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.tick_params('both', length=10, width=1.2, which='major', direction='in')
    ax.tick_params('both', length=5, width=1, which='minor', direction='in')
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    ax.set_ylabel('Depth(m)', fontsize=14)

def plot_NUM_Temp(exp, region, obs, dep):
    print ('plots for ' + exp + ' Region: ' + regions[region].strip() + ' Param: Temperature obs number ')
    if exp.upper() == suite.upper():
        var = count_T
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = count_ref_T
        title = suite_ref_title
    if dep == 2000:
        ix = np.argmax(depth > 2000)
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument ..')
    zz, tt = np.meshgrid(-depth[:ix+1], numdates)
    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = var[:, region, :ix+1].copy().min()
    xx = var[:, region, :ix+1].copy().max()
    ticks = np.linspace(nn, xx, 20).astype(int)
    levels = np.linspace(nn, xx, len(ticks))
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap)
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)
    ax.set_title(obs + ': NUM(DATA) - Temperature - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %8d ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %8d ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs +'_' + start_date + '_' + final_date + '_' + title + '_NUM_DATA_' + str(region) + '_Temp_' + str(dep) + '.png', dpi=80)
    plt.close()


def plot_NUM_Sal(exp, region, obs, dep):
    print ('plots for  ' + exp + ' Region : ' + regions[region].strip() + ' Param: Salinity obs number ')
    if exp.upper() == suite.upper():
        var = count_S
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = count_ref_S
        title = suite_ref_title
# Select depth argument
    if dep == 2000:
        ix = np.argmax(depth > 2000) 
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument')
    zz, tt = np.meshgrid(-depth[:ix+1], numdates)
    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = var[:, region, :ix+1].copy().min()
    xx = var[:, region, :ix+1].copy().max()
    ticks = np.linspace(nn, xx, 20).astype(int)
    levels = np.linspace(nn, xx, len(ticks))
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap)
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)

    ax.set_title(obs + ': NUM(DATA) - Temperature - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %8d ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %8d ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs + '_' + start_date + '_' + final_date + '_' + title + '_NUM_DATA_' + str(region) + '_Sal_' + str(dep) + '.png', dpi=80)
    plt.close()


def plot_MISFIT_AVR_temp(exp, region, obs, dep):
    print ('plots for  ' + exp + ' Region : ' + regions[region].strip() + ' Param: Temp AVR Misfit')
    if exp.upper() == suite.upper():
        var = omp_T
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = omp_ref_T
        title = suite_ref_title
    
# Select depth argument
    if dep == 2000:
        ix = np.argmax(depth > 2000)
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument')

    zz, tt = np.meshgrid(-depth[:ix+1], numdates)
    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = np.nanmin(var[:, region, :ix+1].copy())
    xx = np.nanmax(var[:, region, :ix+1].copy())
    ticks = np.arange(-1.0, 1.01, 0.1)
    levels = np.arange(-1.0, 1.01, 0.05)
    var[:, region, :ix+1][var[:, region, :ix+1] <= -1.0] = -1.0
    var[:, region, :ix+1][var[:, region, :ix+1] >= 1.0] = 1.0
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap, extend='both')
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)
    ax.set_title(obs + ': AVR(MISFIT) - Temperature - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %.5f ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %.5f ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    clb = plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    clb.set_label('deg.', labelpad=-25, y=1.02, rotation=0, fontsize=12)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs + '_' + start_date + '_' + final_date + '_' + title + '_AVR_MISFIT_' + str(region) + '_Temp_' + str(dep) + '.png', dpi=80)
    plt.close()


def plot_MISFIT_AVR_Sal(exp, region, obs, dep):
    print ('plots for ' + exp + ' Region : ' + regions[region].strip() + ' Param: Salinity AVR Misfit')
    if exp.upper() == suite.upper():
        var = omp_S
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = omp_ref_S
        title = suite_ref_title

    # Select depth argument
    if dep == 2000:
        ix = np.argmax(depth > 2000)
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument')

    zz, tt = np.meshgrid(-depth[:ix+1], numdates)
    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = np.nanmin(var[:, region, :ix+1].copy())
    xx = np.nanmax(var[:, region, :ix+1].copy())
    ticks = np.arange(-0.2, 0.21, 0.02)
    levels = np.arange(-0.2, 0.21, 0.01)
    var[:, region, :ix+1][var[:, region, :ix+1] <= -0.2] = -0.2
    var[:, region, :ix+1][var[:, region, :ix+1] >= 0.2] = 0.2
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap, extend='both')
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)
    ax.set_title(obs + ': AVR(MISFIT) - Salinity - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %.5f ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %.5f ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    clb = plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    clb.set_label('Psu', labelpad=-25, y=1.02, rotation=0, fontsize=12)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs + '_' + start_date + '_' + final_date + '_' + title + '_AVR_MISFIT_' + str(region) + '_Sal_' + str(dep) +'.png', dpi=80)
    plt.close()


def plot_MISFIT_RMS_Temp(exp, region, obs, dep):
    print ('plots for ' + exp + ' Region : ' + regions[region].strip() + ' Param: Temp Misfit RMS')
    if exp.upper() == suite.upper():
        var = rms_T
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = rms_ref_T
        title = suite_ref_title

    # Select depth argument
    if dep == 2000:
        ix = np.argmax(depth > 2000)
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument')

    zz, tt = np.meshgrid(-depth[:ix+1], numdates)
    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = np.nanmin(var[:, region, :ix+1].copy())
    xx = np.nanmax(var[:, region, :ix+1].copy())
    ticks = np.arange(0.04, 1.5, 0.070)
    levels = np.arange(0.04, 1.5, 0.035)
    var[:, region, :ix+1][var[:, region, :ix+1] <= 0.04] = 0.04
    var[:, region, :ix+1][var[:, region, :ix+1] >= 1.5] = 1.5
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap, extend='both')
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)
    ax.set_title(obs + ': RMS(MISFIT) - Temperature - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %.5f ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %.5f ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    clb = plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    clb.set_label('deg.', labelpad=-25, y=1.02, rotation=0, fontsize=12)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs + '_' + start_date + '_' + final_date + '_' + title + '_RMS_MISFIT_' + str(region) + '_Temp_' + str(dep) + '.png', dpi=80)
    plt.close()


def plot_MISFIT_RMS_Sal(exp, region, obs, dep):
    print ('plots for ' + exp + ' Region : ' + regions[region].strip() + ' Param: Salinity Misfit RMS')
    if exp.upper() == suite.upper():
        var = rms_S
        title = suite_title
    elif exp.upper() == suite_ref.upper():
        var = rms_ref_S
        title = suite_ref_title

    # Select depth argument
    if dep == 2000:
        ix = np.argmax(depth > 2000)
    elif dep == 200:
        ix = np.argmax(depth > 200)
    else:
        print('Wrong or missing depth argument')
    zz, tt = np.meshgrid(-depth[:ix+1], numdates)

    f, ax = plt.subplots(1, figsize=(15, 10))
    nn = np.nanmin(var[:, region, :ix+1].copy())
    xx = np.nanmax(var[:, region, :ix+1].copy())
    ticks = np.arange(0.01, 0.41, 0.02)
    levels = np.arange(0.01, 0.41, 0.01)
    var[:, region, :ix+1][var[:, region, :ix+1] <= 0.01] = 0.01
    var[:, region, :ix+1][var[:, region, :ix+1] >= 0.40] = 0.40
    cs = ax.contourf(tt, zz, var[:, region, :ix+1], levels=levels, cmap=cmap, extend='both')
    if dep == 2000:
        plot_setup_2000(ax)
    elif dep == 200:
        plot_setup_200(ax)
    # ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    ax.set_title(obs + ': RMS(MISFIT) - Salinity - ' + title, fontsize=18)
    ax.text(0.05, -0.06, regions[region], horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.6, -0.06, 'Min= %.5f ' % (nn), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    ax.text(0.8, -0.06, 'Max= %.5f ' % (xx), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=14)
    clb = plt.colorbar(cs, ticks=ticks, orientation="vertical", pad=0.05)
    clb.set_label('Psu', labelpad=-25, y=1.02, rotation=0, fontsize=12)
    if exp.upper() == suite.upper():
        out_path = output_path
    else:
        out_path = ref_output_path
    plt.savefig(out_path + '/INSITU/' + obs + '_' + start_date + '_' + final_date + '_' + title + '_RMS_MISFIT_' + str(region) + '_Sal_' + str(dep) + '.png', dpi=80)
    plt.close()

def plot_mean_temp(dep):
    ## Temperature (OMP and RMS)
    ix = np.argmax(depth > int(dep))
    f, ax = plt.subplots(1, figsize=(6, 10))
    ax.plot(omp_T_mean[reg, :ix+1], -depth[:ix+1], '--', color='r', linewidth=1.5, label='AVR(MISFIT) ' + suite_title)
    ax.plot(omp_ref_T_mean[reg, :ix+1], -depth[:ix+1], '--', color='b', linewidth=1.5, label='AVR(MISFIT) ' + suite_ref_title)
    ax.plot(rms_T_mean[reg, :ix+1], -depth[:ix+1], '-', color='r', linewidth=1.5, label='RMS(MISFIT) ' + suite_title)
    ax.plot(rms_ref_T_mean[reg, :ix+1], -depth[:ix+1], '-', color='b', linewidth=1.5,  label='RMS(MISFIT) ' + suite_ref_title)
    if dep == 2000:
        mean_plot_setup_2000(ax)
    if dep == 200:
        mean_plot_setup_200(ax)
    ax.xaxis.set_minor_locator(MultipleLocator(0.5))
    ax.xaxis.set_major_locator(MultipleLocator(1.0))
    ax.set_xlim([-2, 2])
    ax.axvline(x=0, linewidth=0.5, color='k')
    ax.set_title(vp + ': Temperature(deg)', fontsize=16)
    if dep == 2000:
        ax.text(-2.0, -int(dep)-100, regions[reg], fontsize=16)
    if dep == 200:
        ax.text(-2.0, -int(dep)-10, regions[reg], fontsize=16)
    plt.legend(bbox_to_anchor=(1.0, 0.0), loc="lower right", bbox_transform=f.transFigure, ncol=2, fontsize=11, frameon=False)
    plt.subplots_adjust(left=0.15, bottom=0.12, right=0.99, top=0.95)
    plt.savefig(output_path + '/INSITU/' + vp + '_' + start_date + '_' + final_date + '_' + suite_title + '_RMS_MISFIT_' + str(reg) + '_Mean_Temp_' + str(dep) + '.png', dpi=80)
    plt.close('all')

def plot_mean_sal(dep):
    ## Salinity (OMP and RMS)
    ix = np.argmax(depth > int(dep))
    f, ax = plt.subplots(1, figsize=(6, 10))
    ax.plot(omp_S_mean[reg, :ix+1], -depth[:ix+1], '--', color='r', linewidth=1.5, label='AVR(MISFIT) ' + suite_title)
    ax.plot(omp_ref_S_mean[reg, :ix+1], -depth[:ix+1], '--', color='b', linewidth=1.5, label='AVR(MISFIT) ' + suite_ref_title)
    ax.plot(rms_S_mean[reg, :ix+1], -depth[:ix+1], '-', color='r', linewidth=1.5, label='RMS(MISFIT) ' + suite_title)
    ax.plot(rms_ref_S_mean[reg, :ix+1], -depth[:ix+1], '-', color='b', linewidth=1.5,  label='RMS(MISFIT) ' + suite_ref_title)
    if dep == 2000:
        mean_plot_setup_2000(ax)
    if dep == 200:
        mean_plot_setup_200(ax)
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(MultipleLocator(0.05))
    ax.set_xlim([-0.5, 0.5])
    ax.axvline(x=0, linewidth=0.5, color='k')
    ax.set_title(vp + ': Salinity(Psu)', fontsize=16)
    if dep == 2000:
        ax.text(-2.0, -int(dep)-100, regions[reg], fontsize=16)
    if dep == 200:
        ax.text(-2.0, -int(dep)-10, regions[reg], fontsize=16)
    plt.legend(bbox_to_anchor=(1.0, 0.0), loc="lower right", bbox_transform=f.transFigure, ncol=2, fontsize=11, frameon=False)
    plt.subplots_adjust(left=0.15, bottom=0.12, right=0.99, top=0.95)
    plt.savefig(output_path + '/INSITU/' + vp + '_' + start_date + '_' + final_date + '_' + suite_title + '_RMS_MISFIT_' + str(reg) + '_Mean_Sal_' + str(dep) + '.png', dpi=80)
    plt.close('all')

def plot_mean_num_temp(dep):
    ### Temperature
    ix = np.argmax(depth > int(dep))
    f, ax = plt.subplots(1, figsize=(6, 10))
    ax.plot(count_T_mean[reg, :ix+1], -depth[:ix+1], '-', color='r', linewidth=1.5, label=suite_title)
    ax.plot(count_ref_T_mean[reg, :ix+1], -depth[:ix+1], '-', color='b', linewidth=1.5, label=suite_ref_title)
    if dep == 2000:
        mean_plot_setup_2000(ax)
    if dep == 200:
        mean_plot_setup_200(ax)
    ax.set_xlim([0, count_T_mean[reg, :ix+1].max()])
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6, steps=[5, 10]))
    ax.xaxis.set_minor_locator(MaxNLocator(nbins=6, steps=[1, 10]))
    ax.set_title(vp + ': Temperature NUM(DATA)', fontsize=16)
    if dep == 2000:
        ax.text(-2.0, -int(dep)-100, regions[reg], fontsize=16)
    if dep == 200:
        ax.text(-2.0, -int(dep)-10, regions[reg], fontsize=16)
    plt.legend(bbox_to_anchor=(0.66, 0.015), loc="lower right", bbox_transform=f.transFigure, ncol=2, fontsize=12, frameon=False)
    plt.subplots_adjust(left=0.15, bottom=0.12, right=0.99, top=0.95)
    plt.savefig(output_path + '/INSITU/' + vp + '_' + start_date + '_' + final_date + '_' + suite_title + '_NUM_DATA_' + str(reg) + '_Mean_Temp_' + str(dep) + '.png', dpi=80)
    plt.close('all')

def plot_mean_num_sal(dep):    
    ### Salinity
    ix = np.argmax(depth > int(dep))
    f, ax = plt.subplots(1, figsize=(6, 10))
    ax.plot(count_S_mean[reg, :ix+1], -depth[:ix+1], '-', color='r', linewidth=1.5, label=suite_title)
    ax.plot(count_ref_S_mean[reg, :ix+1], -depth[:ix+1], '-', color='b', linewidth=1.5, label=suite_ref_title)
    if dep == 2000:
        mean_plot_setup_2000(ax)
    if dep == 200:
        mean_plot_setup_200(ax)
    ax.set_xlim([0, count_S_mean[reg, :ix+1].max()])
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6, steps=[5, 10]))
    ax.xaxis.set_minor_locator(MaxNLocator(nbins=6, steps=[1, 10]))
    ax.set_title(vp + ': Salinity NUM(DATA)', fontsize=16)
    ax.text(0, -int(dep)-100, regions[reg], fontsize=16)
    plt.legend(bbox_to_anchor=(0.66, 0.015), loc="lower right", bbox_transform=f.transFigure, ncol=2, fontsize=12, frameon=False)
    plt.subplots_adjust(left=0.15, bottom=0.12, right=0.99, top=0.95)
    plt.savefig(output_path + '/INSITU/' + vp + '_' + start_date + '_' + final_date + '_' + suite_title + '_NUM_DATA_' + str(reg) + '_Mean_Sal_' + str(dep) + '.png', dpi=80)
    plt.close('all')



# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite", required=True, help="Experiment name")
ap.add_argument("--ref_suite", required=True, help="Reference experiment name")
ap.add_argument("--path", required=True, help="Experiment path")
ap.add_argument("--ref_path", required=True, help="Reference experiment path")
ap.add_argument("--start_date", required=True, help="Start date")
ap.add_argument("--final_date", required=True, help="Final date")
ap.add_argument("--output_path", required=True, help="Output folder path")
ap.add_argument("--ref_output_path", required=True, help="Ref Output folder path")
ap.add_argument("--stype",       required=True, help="Experiment type W(weekly) or D(daily)")

suite = ap.parse_args().suite
suite_ref = ap.parse_args().ref_suite
path = ap.parse_args().path
path_ref = ap.parse_args().ref_path
start_date = ap.parse_args().start_date
final_date = ap.parse_args().final_date
output_path = ap.parse_args().output_path
ref_output_path = ap.parse_args().ref_output_path
exp_id      = ap.parse_args().stype

sdate = datetime.datetime.strptime(start_date, "%Y%m%d")
fdate = datetime.datetime.strptime(final_date, "%Y%m%d")

# Make sure dates are in order
if sdate >= fdate:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)

# Make sure paths end with /
if not path.endswith('/'):
    path = path + '/'
if not path_ref.endswith('/'):
    path_ref = path_ref + '/'

print 'Suite       = ', suite
print 'Ref Suite   = ', suite_ref
print 'Path        = ', path
print 'Ref path    = ', path_ref
print 'Start date  = ', start_date
print 'Final date  = ', final_date
print 'Output path = ', output_path
print 'Experiment type = ', exp_id.upper()



suite_title = suite
suite_ref_title = suite_ref

# Number of dates during the cycle
num_days = (fdate - sdate).days

# List of dates of the cycle
if exp_id.upper() == 'W':
    dates = [sdate + datetime.timedelta(days=x) for x in range(0, num_days + 7, 7)]
elif exp_id.upper() == 'D':
    dates = [sdate + datetime.timedelta(days=x) for x in range(0, num_days + 1)]
dates_nb = len(dates)

# Retrieve regions
with open('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_regions', 'r') as f:
    x = f.readlines()
regions = [line.rstrip('\n') for line in x]
regions_nb = len(regions)
region_num = [str(item).zfill(2) for item in range(0, regions_nb)]  # The 47 regions (2 digits number)

# Retrieve model depths
depth = np.loadtxt('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_depths')
depth_nb = len(depth)

# Instruments (obs) list
d = pd.read_csv('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/VP_observations', header=None)
list_obs = []
for k in d.index:
    if d[1][k]:
        list_obs.append(d[0][k].strip())

# Create output path
try:
    os.makedirs(output_path + '/INSITU')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
try:
    os.makedirs(ref_output_path + '/INSITU')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Loop over list_obs
for vp in list_obs[:]:
    # Arrays initialization
    # Experience
    count_T = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=int)
    count_S = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=int)
    omp_T =   np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    omp_S =   np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    rms_T =   np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    rms_S =   np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    # Reference
    count_ref_T = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=int)
    count_ref_S = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=int)
    omp_ref_T   = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    omp_ref_S   = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    rms_ref_T   = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)
    rms_ref_S   = np.zeros(shape=(dates_nb, regions_nb, depth_nb), dtype=float)

    # Read data and store in numpy arrays, ignore misfit values where nobs=0
    for num_dates in range(dates_nb):
        dateS = datetime.datetime.strftime(dates[num_dates], "%Y%m%d")
        print vp, dateS
        df = read_file(path, suite, dateS, vp)
        df_ref = read_file(path_ref, suite_ref, dateS, vp)
        # Ignore stats where nobs=0
        df['MS(MISFIT)'].loc[df['DATA'] == 0.0] = np.nan
        df['AVR(MISFIT)'].loc[df['DATA'] == 0.0] = np.nan
        df_ref['MS(MISFIT)'].loc[df_ref['DATA'] == 0.0] = np.nan
        df_ref['AVR(MISFIT)'].loc[df_ref['DATA'] == 0.0] = np.nan

        for reg in range(regions_nb):
            count_T[num_dates, reg] = df[df['MASK'] == reg]['DATA'][1:depth_nb+1]
            count_S[num_dates, reg] = df[df['MASK'] == reg]['DATA'][depth_nb+1:2*depth_nb+1]
            omp_T[num_dates, reg] = df[df['MASK'] == reg]['AVR(MISFIT)'][1:depth_nb+1]
            omp_S[num_dates, reg] = df[df['MASK'] == reg]['AVR(MISFIT)'][depth_nb+1:2*depth_nb+1]
            rms_T[num_dates, reg] = np.sqrt(df[df['MASK'] == reg]['MS(MISFIT)'][1:depth_nb+1])
            rms_S[num_dates, reg] = np.sqrt(df[df['MASK'] == reg]['MS(MISFIT)'][depth_nb+1:2*depth_nb+1])
            count_ref_T[num_dates, reg] = df_ref[df_ref['MASK'] == reg]['DATA'][1:depth_nb+1]
            count_ref_S[num_dates, reg] = df_ref[df_ref['MASK'] == reg]['DATA'][depth_nb+1:2*depth_nb+1]
            omp_ref_T[num_dates, reg] = df_ref[df_ref['MASK'] == reg]['AVR(MISFIT)'][1:depth_nb+1]
            omp_ref_S[num_dates, reg] = df_ref[df_ref['MASK'] == reg]['AVR(MISFIT)'][depth_nb+1:2*depth_nb+1]
            rms_ref_T[num_dates, reg] = np.sqrt(df_ref[df_ref['MASK'] == reg]['MS(MISFIT)'][1:depth_nb+1])
            rms_ref_S[num_dates, reg] = np.sqrt(df_ref[df_ref['MASK'] == reg]['MS(MISFIT)'][depth_nb+1:2*depth_nb+1])

    # Temporal averages
    ##suite
    count_T_mean = np.nanmean(count_T, axis=0)
    count_S_mean = np.nanmean(count_S, axis=0)
    omp_T_mean = np.nanmean(omp_T, axis=0)
    omp_S_mean = np.nanmean(omp_S, axis=0)
    rms_T_mean = np.nanmean(rms_T, axis=0)
    rms_S_mean = np.nanmean(rms_S, axis=0)
    ## reference
    count_ref_T_mean = np.nanmean(count_ref_T, axis=0)
    count_ref_S_mean = np.nanmean(count_ref_S, axis=0)
    omp_ref_T_mean = np.nanmean(omp_ref_T, axis=0)
    omp_ref_S_mean = np.nanmean(omp_ref_S, axis=0)
    rms_ref_T_mean = np.nanmean(rms_ref_T, axis=0)
    rms_ref_S_mean = np.nanmean(rms_ref_S, axis=0)

    # Graphics production
    numdates = date2num(dates)
    wednesdays = WeekdayLocator(WEDNESDAY)  # tick on wednesday every week (not used)
    cmap = cm.get_cmap("jet", 50)  # Color palette

    #index of first depth > 2000m
    ix_2000 = np.argmax(depth > 2000)
    zz_2000, tt_2000 = np.meshgrid(-depth[:ix_2000+1], numdates)
    
    #index of first depth > 200m
    ix_200 = np.argmax(depth > 200)
    zz_200, tt_200 = np.meshgrid(-depth[:ix_200+1], numdates)

    for reg in range(regions_nb):
        print 'plots for ' + regions[reg].strip()

        ## Temperature (2000m)
        if count_T[:, reg, :ix_2000+1].max() > 0:
            plot_NUM_Temp(suite, reg, vp, 2000)         # Obs number
            plot_MISFIT_AVR_temp(suite, reg, vp, 2000)  # Misfit avg
            plot_MISFIT_RMS_Temp(suite, reg, vp, 2000)  # Misfit RMS
        if count_ref_T[:, reg, :ix_2000+1].max() > 0:
            plot_NUM_Temp(suite_ref, reg, vp, 2000)        # Obs number
            plot_MISFIT_AVR_temp(suite_ref, reg, vp, 2000) # Misfit avg
            plot_MISFIT_RMS_Temp(suite_ref, reg, vp, 2000) # Misfit RMS

        ## Temperature (200m)
        if count_T[:, reg, :ix_200+1].max() > 0:
            plot_NUM_Temp(suite, reg, vp, 200)         # Obs number
            plot_MISFIT_AVR_temp(suite, reg, vp, 200)  # Misfit avg
            plot_MISFIT_RMS_Temp(suite, reg, vp, 200)  # Misfit RMS
        if count_ref_T[:, reg, :ix_200+1].max() > 0:
            plot_NUM_Temp(suite_ref, reg, vp, 200)        # Obs number
            plot_MISFIT_AVR_temp(suite_ref, reg, vp, 200) # Misfit avg
            plot_MISFIT_RMS_Temp(suite_ref, reg, vp, 200) # Misfit RMS

        ## Salinity (2000m)
        if count_S[:, reg, :ix_2000+1].max() > 0:
            plot_NUM_Sal(suite, reg, vp, 2000)          # Obs number
            plot_MISFIT_AVR_Sal(suite, reg, vp, 2000)   # Misfit avg
            plot_MISFIT_RMS_Sal(suite, reg, vp, 2000)   # Misfit RMS
        if count_ref_S[:, reg, :ix_2000+1].max() > 0:
            plot_NUM_Sal(suite_ref, reg, vp, 2000)        # Obs number
            plot_MISFIT_AVR_Sal(suite_ref, reg, vp, 2000) # Misfit avg
            plot_MISFIT_RMS_Sal(suite_ref, reg, vp, 2000) # Misfit RMS

        ## Salinity (200m)
        if count_S[:, reg, :ix_200+1].max() > 0:
            plot_NUM_Sal(suite, reg, vp, 200)          # Obs number
            plot_MISFIT_AVR_Sal(suite, reg, vp, 200)   # Misfit avg
            plot_MISFIT_RMS_Sal(suite, reg, vp, 200)   # Misfit RMS
        if count_ref_S[:, reg, :ix_200+1].max() > 0:
            plot_NUM_Sal(suite_ref, reg, vp, 200)        # Obs number
            plot_MISFIT_AVR_Sal(suite_ref, reg, vp, 200) # Misfit avg
            plot_MISFIT_RMS_Sal(suite_ref, reg, vp, 200) # Misfit RMS
#KC ---A terminer
    # Temporal means graphics
    for reg in range(regions_nb):
        print 'Mean profile plot for :', regions[reg].strip()
        ## Temperature (OMP and RMS)
        plot_mean_temp(2000)
        plot_mean_temp(200)
          
        ## Salinity (OMP and RMS)
        plot_mean_sal(2000)
        plot_mean_sal(200)
        
        ## NUM(DATA)
        ### Temperature
        plot_mean_num_temp(2000)
        plot_mean_num_temp(200)

        ### Salinity
        plot_mean_num_sal(2000)
        plot_mean_num_sal(200)
