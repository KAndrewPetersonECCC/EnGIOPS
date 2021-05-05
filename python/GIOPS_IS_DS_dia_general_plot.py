'''
Author: Kamel Chikhar

Purpose: plot misfit statistics time series
Input: SAM2 cycle DIA files

'''

# Import needed modules
import argparse
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullLocator
from matplotlib.dates import date2num, DateFormatter, YearLocator, MonthLocator, WeekdayLocator, WEDNESDAY, DayLocator
import matplotlib.dates as mdates
import sys
import os
import os.path
import errno
import time
from scipy import stats
from matplotlib.patches import Rectangle

initial_time = time.time()

# Define functions
def read_file(path, date, obs):
    '''
    function to read statistic data from SAM/DIA file
    Input: date: analysis date
    suite: suite name
    path: suite path
    obs: obs name
    Output: Numpy array containing the dia data
    '''
    infile = path + '/' + date + '/DIA/' + date + '00_SAM.dia_' + obs

    if os.path.isfile(infile):
        return pd.read_csv(infile, skiprows=2, delim_whitespace=True, na_values=['-0.17977+309'], usecols=(3, 5, 7))
    elif os.path.isfile(infile + '.gz'):
        return pd.read_csv(infile + '.gz', compression='gzip', skiprows=2, delim_whitespace=True, na_values=['-0.17977+309'], usecols=(3, 5, 7))
    else:
        sys.exit(infile + "does not exist")
        

def filter_zeros_avg(df):
    '''
    Filter dates with zeros data number and compute columns means
    input: pandas dataframe
    '''
    for i in np.arange(len(regions)):
        df['omp_'+str(i).zfill(2)].loc[df['nobs_'+str(i).zfill(2)] <= 0] = np.nan
        df['rms_'+str(i).zfill(2)].loc[df['nobs_'+str(i).zfill(2)] <= 0] = np.nan
        df['nobs_'+str(i).zfill(2)].loc[df['nobs_'+str(i).zfill(2)] < 0] = np.nan
    cols = df.columns.get_values().tolist()
    df_m = df
    return df_m[cols].mean()

def plot_timeseries(reg, df, df_ref, obs, cycle, ref_cycle):
    f, [ax1, ax2, ax3] = plt.subplots(3, figsize=(12, 10))
    plt.subplots_adjust(hspace=0.4)
    if obs in ['GEN_SST', 'GEN_SST_night']:
        plt.suptitle(obs + ' diagnostics', fontsize=14)
    else:
        plt.suptitle('SLA-' + obs + ' diagnostics', fontsize=14)

    # NUM DATA
    ax1.plot(df.index, df['nobs_'+reg], color='r', linewidth=1.5, linestyle='-', label=cycle)
    ax1.plot(df_ref.index, df_ref['nobs_'+reg], color='b', linewidth=1.5, linestyle='-', label=ref_cycle)
    ax1.set_title('NUM(DATA)', fontsize=14, horizontalalignment='left')
    ax1.set_ylim([0, df['nobs_'+reg].max() + df['nobs_'+reg].max()/10.])
    ax1.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax1.text(0.0, 1.02, reg + '-' + regions[int(reg)], size=14, ha="left", transform=ax1.transAxes)
    ax1.legend(fontsize=14)

    # OMP
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax2.plot(df.index, df['omp_'+reg], color='r', linewidth=1.5, linestyle='-')
        ax2.plot(df_ref.index, df_ref['omp_'+reg], color='b', linewidth=1.5, linestyle='-')
    else:
        ax2.plot(df.index, df['omp_'+reg]*100, color='r', linewidth=1.5, linestyle='-')
        ax2.plot(df_ref.index, df_ref['omp_'+reg]*100, color='b', linewidth=1.5, linestyle='-')

    ax2.set_title('AVR(MISFIT)', fontsize=14, horizontalalignment='left')
    ax2.axhline(y=0, linewidth=1, color='k', zorder=0)
    ax2.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax2.set_ylim([-1, 1])
        ax2.set_ylabel('deg', fontsize=14, horizontalalignment='left')
        ax2.set_yticks(np.arange(-1, 1.1, 0.2))
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
        ax2.yaxis.set_major_locator(MultipleLocator(0.5))
        ax2.yaxis.set_minor_locator(MultipleLocator(0.1))
    else:
        ax2.set_ylim([-6, 6])
        ax2.set_ylabel('cm', fontsize=14, horizontalalignment='left')
        ax2.set_yticks(np.arange(-6, 6.1, 1.0))
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%1d'))
        ax2.yaxis.set_major_locator(MultipleLocator(2.0))
        ax2.yaxis.set_minor_locator(MultipleLocator(1.0))

    # RMS
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax3.plot(df.index, df['rms_'+reg], color='r', linewidth=1.5, linestyle='-')
        ax3.plot(df_ref.index, df_ref['rms_'+reg], color='b', linewidth=1.5, linestyle='-')
    else:
        ax3.plot(df.index, df['rms_'+reg]*100, color='r', linewidth=1.5, linestyle='-')
        ax3.plot(df_ref.index, df_ref['rms_'+reg]*100, color='b', linewidth=1.5, linestyle='-')
    ax3.set_title('RMS(MISFIT)', fontsize=14, horizontalalignment='left')
    ax3.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax3.set_ylabel('deg', fontsize=14, horizontalalignment='left')
        ax3.set_ylim([0, 2])
        ax3.set_yticks(np.arange(0, 2.1, 0.2))
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
        ax3.yaxis.set_major_locator(MultipleLocator(0.5))
        ax3.yaxis.set_minor_locator(MultipleLocator(0.1))
    else:
        ax3.set_ylabel('cm', fontsize=14, horizontalalignment='left')
        ax3.set_ylim([0, 30])
        ax3.set_yticks(np.arange(0, 30.1, 1))
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax3.yaxis.set_major_locator(MultipleLocator(5.0))
        ax3.yaxis.set_minor_locator(MultipleLocator(1.0))

    if num_days<= 366:
        for ax in [ax1,ax2, ax3]:
            fig_setup_monthly(ax)
    if num_days > 366:
        for ax in [ax1, ax2, ax3]:
            fig_setup_yearly(ax)
    if num_days <= 366 and exp_id == "D":
        for ax in [ax1, ax2, ax3]:
            fig_setup_weekly(ax)


    
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_' + str(int(reg)) + '.png', dpi=80)
    print 'Done for ' + obs + '...' + regions[int(reg)]
    plt.close()

def plot_mean_stat(data, data_ref, obs, cycle, cycle_ref, p):
    '''
    Function to plot statistics
    Input:
    data: data to plot (dataframe of each obs)
    data_ref: reference data
    '''
    nregs = len(regions)
    nregs_N = len(regions_N)
    nregs_S = len(regions_S)
    if obs in ['ALTIKA', 'CRYOSAT2', 'JASON2', 'JASON3', 'JASON2N', 'HY2A', 'SENTINEL3A', 'SENTINEL3B']:
        data[nregs:] = data[nregs:] * 100                       # convert to cm
        data_ref[nregs:] = data_ref[nregs:] * 100               # convert to cm
    y1 = np.arange(0, nregs_N*2, 2)
    y2 = np.arange(0, nregs_S*2, 2)
    width1 = [0.5] * len(y1)
    width2 = [0.5] * len(y2)
    width3 = [1.0] * len(y1)
    width4 = [1.0] * len(y2)
    # Num data
    fig1 = plt.figure(figsize=(8, 10)); ax = fig1.gca()
    ax.barh(y1, data[1:nregs_N+1], width1,  align='center', color='red')
    ax.barh(y1+width1, data_ref[1:nregs_N+1], width1,  align='center', color='blue')
    ax.set_yticks(y1+0.25)
    ax.set_ylim([-1, y1[-1]+1])
    ax.set_yticklabels(regions_N, fontsize=14)
    ax.set_title('Average NUM(DATA)', fontsize=16)
    ax.text(0, y1[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax.legend((cycle, cycle_ref))
    if not np.isnan(data[0]):
        ax.set_xlabel('Global = %8d            Global(ref) = %8d' %(data[0], data_ref[0]))
    else:
        ax.set_xlabel('Global = Nan            Global(ref) = Nan')
    fig1.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_NUM_DATA_Mean_N.png', dpi=80)
    plt.close()

    fig2 = plt.figure(figsize=(8, 10)); ax = fig2.gca()
    ax.barh(y2, data[nregs_N+1:nregs], width2,  align='center', color='red')
    ax.barh(y2+width2, data_ref[nregs_N+1:nregs], width2,  align='center', color='blue')
    ax.set_yticks(y2+0.25)
    ax.set_ylim([-1, y2[-1]+1])
    ax.set_yticklabels(regions_S, fontsize=14)
    ax.set_title('Average NUM(DATA)', fontsize=16)
    ax.text(0, y2[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax.legend((cycle, cycle_ref))
    if not np.isnan(data[0]):
        ax.set_xlabel('Global = %8d            Global(ref) = %8d' %(data[0], data_ref[0]), fontsize=14)
    else:
        ax.set_xlabel('Global = NaN            Global(ref) = NaN')

    fig2.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_NUM_DATA_Mean_S.png', dpi=80)
    plt.close()

    # OMP
    fig1 = plt.figure(figsize=(8, 10)); ax = fig1.gca()
    ax.barh(y1, data[nregs+1:nregs+nregs_N+1], width1,  align='center', color='red')
    ax.barh(y1+width1, data_ref[nregs+1:nregs+nregs_N+1], width1,  align='center', color='blue')
    ax.set_yticks(y1+0.25)
    ax.set_yticklabels(regions_N, fontsize=14)
    ax.set_title('Average AVR(MISFIT)', fontsize=16)
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax.set_xlim([-1, 1])
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    else:
        ax.set_xlim([-6, 6])
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1d'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))

    ax.set_ylim([-1, y1[-1]+1])
    ax.text(ax.get_xlim()[0], y1[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax.legend((cycle, cycle_ref))
    ax.axvline(x=0, linewidth=0.2, color='k')
    if not np.isnan(data[0]):
        ax.set_xlabel('Global = %.5f            Global(ref) = %.5f' %(data[nregs], data_ref[nregs]), fontsize=14)
    else:
        ax.set_xlabel('Global = NaN            Global(ref) = NaN')
    fig1.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_AVR_MISFIT_Mean_N.png', dpi=80)
    plt.close()

    fig2 = plt.figure(figsize=(8, 10)); ax = fig2.gca()
    ax.barh(y2, data[nregs+nregs_N+1:2*nregs], width2,  align='center', color='red')
    ax.barh(y2+width2, data_ref[nregs+nregs_N+1:2*nregs], width2,  align='center', color='blue')
    ax.set_yticks(y2+0.25)
    ax.set_ylim([-1, y2[-1]+1])
    ax.set_yticklabels(regions_S, fontsize=14)
    ax.set_title('Average AVR(MISFIT)', fontsize=16)
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax.set_xlim([-1, 1])
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    else:
        ax.set_xlim([-6, 6])
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1d'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))
    ax.text(ax.get_xlim()[0], y2[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax.legend((cycle, cycle_ref))
    ax.axvline(x=0, linewidth=0.2, color='k')
    if not np.isnan(data[0]):
        ax.set_xlabel('Global = %.5f            Global(ref) = %.5f' %(data[nregs], data_ref[nregs]), fontsize=14)
    else:
        ax.set_xlabel('Global = NaN            Global(ref) = NaN')
    fig2.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_AVR_MISFIT_Mean_S.png', dpi=80)
    plt.close()

    #RMS
    fig1 = plt.figure(figsize=(8, 10))
    ax1 = fig1.gca()
    ax2 = ax1.twiny()
    ax1.barh(y1, data[2*nregs+1:2*nregs+nregs_N+1], width1,  align='center', color='red')
    ax1.barh(y1+width1, data_ref[2*nregs+1:2*nregs+nregs_N+1], width1,  align='center', color='blue')
    ax1.set_yticks(y1+0.25)
    ax1.set_yticklabels(regions_N, fontsize=14)
    ax1.set_title('Average RMS(MISFIT)', fontsize=16)
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax1.set_xlim([0, 2])
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax1.xaxis.set_minor_locator(MultipleLocator(0.1))
        bb = np.array([-0.05] * len(data[2*nregs+1:2*nregs+nregs_N+1]))
        ax2.set_xlim([-1.5, 0])
    else:
        ax1.set_xlim([0, 30])
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%1d'))
        ax1.xaxis.set_minor_locator(MultipleLocator(1.0))
        bb = np.array([-0.5]*len(data[2*nregs+1:2*nregs+nregs_N+1]))
        ax2.set_xlim([-15., 0])

    ax1.set_ylim([-1, y1[-1]+1])
    ax1.text(ax1.get_xlim()[0], y1[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax1.legend((cycle, cycle_ref), loc='upper center')
    if not np.isnan(data[0]):
        ax1.set_xlabel('Global = %.5f            Global(ref) = %.5f' %(data[2*nregs], data_ref[2*nregs]), fontsize=14)
    else:
        ax1.set_xlabel('Global = NaN            Global(ref) = NaN')
    recs = ax2.barh(y1+0.25, bb, width3, align='center', edgecolor='none')
    ax2.xaxis.set_major_locator(NullLocator())
    for i in range(len(recs)):
        if np.isnan(p[i+1]):
            recs[i].set_facecolor("#d8dcd6")
        if p[i+1] <= 0.05 and (data[i+2*nregs+1] > data_ref[i+2*nregs+1]):
            recs[i].set_facecolor('blue')
        if p[i+1] <= 0.05 and (data[i+2*nregs+1] < data_ref[i+2*nregs+1]):
            recs[i].set_facecolor('red')
        if p[i+1] > 0.05 or (data[i+2*nregs+1] == data_ref[i+2*nregs+1]):
            recs[i].set_facecolor("#d8dcd6")

    if obs in ['GEN_SST', 'GEN_SST_night']:
        if p[0] <= 0.05 and (data[2*nregs] > data_ref[2*nregs]):
            ax1.add_patch(Rectangle((1.9, -3.2), 0.05, 1.0, facecolor='blue', edgecolor='none', zorder=6, clip_on=False))
        if p[0] <= 0.05 and (data[2*nregs] < data_ref[2*nregs]):
            ax1.add_patch(Rectangle((1.9, -3.2), 0.05, 1.0, facecolor='red', edgecolor='none', zorder=6, clip_on=False))
        if p[0] > 0.05:
            ax1.add_patch(Rectangle((1.9, -3.2), 0.05, 1.0, facecolor="#d8dcd6", edgecolor='none', zorder=6, clip_on=False))

    if obs not in ['GEN_SST', 'GEN_SST_night']:
        if p[0] <= 0.05 and (data[2*nregs] > data_ref[2*nregs]):
            ax1.add_patch(Rectangle((29.0, -3.2), 1.0, 1.0, facecolor='blue', edgecolor='none', zorder=6, clip_on=False))
        if p[0] <= 0.05 and (data[2*nregs] < data_ref[2*nregs]):
            ax1.add_patch(Rectangle((29.0, -3.2), 1.0, 1.0, facecolor='red', edgecolor='none', zorder=6, clip_on=False))
        if p[0] > 0.05:
            ax1.add_patch(Rectangle((29.0, -3.2), 1.0, 1.0, facecolor="#d8dcd6", edgecolor='none', zorder=6, clip_on=False))
    
    fig1.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_RMS_MISFIT_Mean_N.png', dpi=80)
    plt.close()

    fig2 = plt.figure(figsize=(8, 10))
    ax1 = fig2.gca()
    ax2 = ax1.twiny()
    ax1.barh(y2, data[2*nregs+nregs_N+1:], width2,  align='center', color='red')
    ax1.barh(y2+width2, data_ref[2*nregs+nregs_N+1:], width2,  align='center', color='blue')
    ax1.set_yticks(y2+0.25)
    ax1.set_yticklabels(regions_S, fontsize=14)
    ax1.set_title('Average RMS(MISFIT)', fontsize=16)
    if obs in ['GEN_SST', 'GEN_SST_night']:
        ax1.set_xlim([0, 2])
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax1.xaxis.set_minor_locator(MultipleLocator(0.1))
        bb = np.array([-0.05] * len(data[2*nregs+nregs_N+1:]))
        ax2.set_xlim([-1.5, 0])
    else:
        ax1.set_xlim([0, 30])
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%1d'))
        ax1.xaxis.set_minor_locator(MultipleLocator(1.0))
        bb = np.array([-0.5]*len(data[2*nregs+nregs_N+1:]))
        ax2.set_xlim([-15., 0])
    ax1.set_ylim([-1, y2[-1]+1])
    ax1.text(ax1.get_xlim()[0], y2[-1] + 1.25, obs.replace("_", " "), size=14, ha="left")
    ax1.legend((cycle, cycle_ref),loc='upper center')
    if not np.isnan(data[0]):
        ax1.set_xlabel('Global = %.5f            Global(ref) = %.5f' %(data[2*nregs], data_ref[2*nregs]), fontsize=14)
    else:
        ax1.set_xlabel('Global = NaN            Global(ref) = NaN')
    recs = ax2.barh(y2+0.25, bb, width4, align='center', edgecolor='none')
    ax2.xaxis.set_major_locator(NullLocator())
    for i in range(len(recs)):
        if np.isnan(p[i+nregs_N+1]):
            recs[i].set_facecolor("#d8dcd6")
        if p[i+23] <= 0.05 and (data[i+2*nregs+nregs_N+1] > data_ref[i+2*nregs+nregs_N+1]):
            recs[i].set_facecolor('blue')
        if p[i+23] <= 0.05 and (data[i+2*nregs+nregs_N+1] < data_ref[i+2*nregs+nregs_N+1]):
            recs[i].set_facecolor('red')
        if p[i+23] > 0.05 or (data[i+2*nregs+nregs_N+1] == data_ref[i+2*nregs+nregs_N+1]):
            recs[i].set_facecolor("#d8dcd6")
    if obs in ['GEN_SST', 'GEN_SST_night']:
        if p[0] <= 0.05 and (data[2*nregs] > data_ref[2*nregs]):
            ax1.add_patch(Rectangle((1.9, -3.4), 0.05, 1.0, facecolor='blue', edgecolor='none', zorder=6, clip_on=False))
        if p[0] <= 0.05 and (data[2*nregs] < data_ref[2*nregs]):
            ax1.add_patch(Rectangle((1.9, -3.4), 0.05, 1.0, facecolor='red', edgecolor='none', zorder=6, clip_on=False))
        if p[0] > 0.05 or np.isnan(p[0]):
            ax1.add_patch(Rectangle((1.9, -3.4), 0.05, 1.0, facecolor="#d8dcd6", edgecolor='none', zorder=6, clip_on=False))

    if obs not in ['GEN_SST', 'GEN_SST_night']:
        if p[0] <= 0.05 and (data[2*nregs] > data_ref[2*nregs]):
            ax1.add_patch(Rectangle((29.0, -3.5), 1.0, 1.0, facecolor='blue', edgecolor='none', zorder=6, clip_on=False))
        if p[0] <= 0.05 and (data[2*nregs] < data_ref[2*nregs]):
            ax1.add_patch(Rectangle((29.0, -3.5), 1.0, 1.0, facecolor='red', edgecolor='none', zorder=6, clip_on=False))
        if p[0] > 0.05 or np.isnan(p[0]):
            ax1.add_patch(Rectangle((29.0, -3.5), 1.0, 1.0, facecolor="#d8dcd6", edgecolor='none', zorder=6, clip_on=False))
    fig2.subplots_adjust(left=0.2)
    plt.tight_layout()
    plt.savefig(output_path + '/' + obs +'/' + obs + '_' + start_date + '_' + final_date + '_RMS_MISFIT_Mean_S.png', dpi=80)
    plt.close()
    return

def fig_setup_weekly(ax):
    wednesdays = WeekdayLocator(WEDNESDAY)
    alldays = DayLocator(bymonthday=range(1,32))
    ax.xaxis.set_major_locator(wednesdays)
    ax.xaxis.set_minor_locator(alldays)
    ax.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.tick_params(axis = 'x', which = 'major', labelsize = 10)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=25, ha='right')

def fig_setup_monthly(ax):
    months = mdates.MonthLocator()  # every month
    wednesdays = WeekdayLocator(WEDNESDAY) # every wednesday
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_minor_locator(wednesdays)
    ax.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(axis='both', which='major', labelsize=11)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=25, ha='right')

def fig_setup_daily(ax):
    wednesdays = WeekdayLocator(WEDNESDAY)
    alldays = DayLocator(bymonthday=range(1,32))
    ax.xaxis.set_major_locator(alldays)
    ax.xaxis.set_minor_locator(alldays)
    ax.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.tick_params(axis = 'x', which = 'major', labelsize = 8)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=25, ha='right')

def fig_setup_yearly(ax):
    years = YearLocator(month=1, day=1)    # every year
    months = MonthLocator(bymonthday=1)  # every month
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_minor_locator(months)
    ax.set_xlim(pd.Timestamp(start_date), pd.Timestamp(final_date))
    ax.xaxis.set_major_formatter(DateFormatter('\n%Y'))
    ax.xaxis.set_minor_formatter(DateFormatter('%m'))
    ax.tick_params(axis='x', which='minor', labelsize=8)
    ax.tick_params(axis='x', which='major', length=0)
    ax.tick_params(axis='both', which='major', labelsize=11)



# Setting and parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument("--suite",       required=True, help="Experiment name")
ap.add_argument("--ref_suite",   required=True, help="Reference experiment name")
ap.add_argument("--path",        required=True, help="Experiment path")
ap.add_argument("--ref_path",    required=True, help="Reference experiment path")
ap.add_argument("--start_date",  required=True, help="Start date YYYYMMDD")
ap.add_argument("--final_date",  required=True, help="Final date YYYYMMDD")
ap.add_argument("--output_path", required=True, help="Output folder path")
ap.add_argument("--stype",       required=True, help="Experiment type W(weekly) or D(daily)")

suite       = ap.parse_args().suite
ref_suite   = ap.parse_args().ref_suite
path        = ap.parse_args().path
ref_path    = ap.parse_args().ref_path
start_date  = ap.parse_args().start_date
final_date  = ap.parse_args().final_date
output_path = ap.parse_args().output_path
exp_id      = ap.parse_args().stype


sdate = datetime.datetime.strptime(start_date, "%Y%m%d")
fdate = datetime.datetime.strptime(final_date, "%Y%m%d")

# Make sure dates are in order
if sdate > fdate:
    print 'Start date >= End date ... Check your date arguments'
    sys.exit(2)

# Make sure exp_id is valid
if (exp_id.upper() != 'D') and (exp_id != 'W'):
    print 'Wrong experiment type ... Must be D or W'
    sys.exit(2)

# Make sure paths end with /
if not path.endswith('/'):
    path = path + '/'
if not ref_path.endswith('/'):
    ref_path = ref_path + '/'
if not output_path.endswith('/'):
    output_path = output_path + '/'

print 'Suite       = ', suite
print 'Ref Suite   = ', ref_suite
print 'Path        = ', path
print 'Ref path    = ', ref_path
print 'Start date  = ', start_date
print 'Final date  = ', final_date
print 'Output path = ', output_path
print 'Exp_id      = ', exp_id

# Number of dates during the cycle
num_days = (fdate - sdate).days


# List of dates of the cycle
if exp_id.upper() == 'W':
    dates = [sdate + datetime.timedelta(days=x) for x in range(0, num_days + 7, 7)]
elif exp_id.upper() == 'D':
    dates = [sdate + datetime.timedelta(days=x) for x in range(0, num_days + 1)]


# Instruments (obs) list
d = pd.read_csv('/home/kch001/my_src/GIOPS/constants/IS_DS_observations', header=None)
list_obs = []
if exp_id.upper() == 'D':
    list_obs = ['GEN_SST','GEN_SST_night']
elif exp_id.upper() == 'W':
    for k in d.index:
        if d[2][k]:
            list_obs.append(d[1][k].strip())

# Retrieve regions
with open('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_regions', 'r') as f:
    x = f.readlines()
regions = [line.rstrip('\n') for line in x]
regions_N = regions[1:23]
regions_S = regions[23:]

# The 47 regions number
region_num = [str(item).zfill(2) for item in range(0, len(regions))]

# Create output path for every instrument
for i in range(len(list_obs)):
    try:
        os.makedirs(output_path + '/' + list_obs[i])
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

# Arrays initialization
count = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=float)
omp   = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=float)
ms    = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=float)

count_ref = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=int)
omp_ref   = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=float)
ms_ref    = np.zeros(shape=(len(list_obs), len(dates), len(regions)), dtype=float)

# Read data and store in numpy arrays
for num_dates in range(len(dates)):
    dateS = datetime.datetime.strftime(dates[num_dates], "%Y%m%d")
    for obs in list_obs:
        print dateS, obs
        infile = path + '/' + dateS + '/DIA/' + dateS + '00_SAM.dia_' + obs
        if os.path.isfile(infile) or os.path.isfile(infile + '.gz'):
            count[list_obs.index(obs), num_dates, :]     = read_file(path, dateS, obs)['DATA']
            count_ref[list_obs.index(obs), num_dates, :] = read_file(ref_path, dateS, obs)['DATA']
            omp[list_obs.index(obs), num_dates, :]       = read_file(path, dateS, obs)['AVR(MISFIT)']
            omp_ref[list_obs.index(obs), num_dates, :]   = read_file(ref_path, dateS, obs)['AVR(MISFIT)']
            ms[list_obs.index(obs), num_dates, :]        = read_file(path, dateS, obs)['MS(MISFIT)']
            ms_ref[list_obs.index(obs), num_dates, :]    = read_file(ref_path, dateS, obs)['MS(MISFIT)']
        else:
            count[list_obs.index(obs), num_dates, :]     = np.nan
            count_ref[list_obs.index(obs), num_dates, :] = np.nan
            omp[list_obs.index(obs), num_dates, :]       = np.nan
            omp_ref[list_obs.index(obs), num_dates, :]   = np.nan
            ms[list_obs.index(obs), num_dates, :]        = np.nan
            ms_ref[list_obs.index(obs), num_dates, :]    = np.nan

# compute RMS
rms = np.sqrt(ms)
rms_ref = np.sqrt(ms_ref)

# Create dataframes
#SST
if 'GEN_SST' in list_obs:
    df_count_SST = pd.DataFrame(count[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_SST   = pd.DataFrame(omp[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['omp_00'])
    df_rms_SST   = pd.DataFrame(rms[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_SST = pd.DataFrame(count_ref[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_SST   = pd.DataFrame(omp_ref[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_SST   = pd.DataFrame(rms_ref[list_obs.index('GEN_SST'), :, 0], index=dates, columns=['rms_00'])

#SST_night
if 'GEN_SST_night' in list_obs:
    df_count_SST_night = pd.DataFrame(count[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_SST_night   = pd.DataFrame(omp[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['omp_00'])
    df_rms_SST_night   = pd.DataFrame(rms[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_SST_night = pd.DataFrame(count_ref[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_SST_night   = pd.DataFrame(omp_ref[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_SST_night   = pd.DataFrame(rms_ref[list_obs.index('GEN_SST_night'), :, 0], index=dates, columns=['rms_00'])

#ALTIKA
if 'ALTIKA' in list_obs:
    df_count_ALTIKA = pd.DataFrame(count[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ALTIKA   = pd.DataFrame(omp[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ALTIKA   = pd.DataFrame(rms[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_ALTIKA = pd.DataFrame(count_ref[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_ALTIKA   = pd.DataFrame(omp_ref[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_ALTIKA   = pd.DataFrame(rms_ref[list_obs.index('ALTIKA'), :, 0], index=dates, columns=['rms_00'])

#CRYOSAT2
if 'CRYOSAT2' in list_obs:
    df_count_CRYOSAT2 = pd.DataFrame(count[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_CRYOSAT2   = pd.DataFrame(omp[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['omp_00'])
    df_rms_CRYOSAT2   = pd.DataFrame(rms[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_CRYOSAT2 = pd.DataFrame(count_ref[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_CRYOSAT2   = pd.DataFrame(omp_ref[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_CRYOSAT2   = pd.DataFrame(rms_ref[list_obs.index('CRYOSAT2'), :, 0], index=dates, columns=['rms_00'])

#JASON2
if 'JASON2' in list_obs:
    df_count_JASON2 = pd.DataFrame(count[list_obs.index('JASON2'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_JASON2   = pd.DataFrame(omp[list_obs.index('JASON2'), :, 0], index=dates, columns=['omp_00'])
    df_rms_JASON2   = pd.DataFrame(rms[list_obs.index('JASON2'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_JASON2 = pd.DataFrame(count_ref[list_obs.index('JASON2'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_JASON2   = pd.DataFrame(omp_ref[list_obs.index('JASON2'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_JASON2   = pd.DataFrame(rms_ref[list_obs.index('JASON2'), :, 0], index=dates, columns=['rms_00'])

#JASON3
if 'JASON3' in list_obs:
    df_count_JASON3 = pd.DataFrame(count[list_obs.index('JASON3'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_JASON3   = pd.DataFrame(omp[list_obs.index('JASON3'), :, 0], index=dates, columns=['omp_00'])
    df_rms_JASON3   = pd.DataFrame(rms[list_obs.index('JASON3'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_JASON3 = pd.DataFrame(count_ref[list_obs.index('JASON3'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_JASON3   = pd.DataFrame(omp_ref[list_obs.index('JASON3'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_JASON3   = pd.DataFrame(rms_ref[list_obs.index('JASON3'), :, 0], index=dates, columns=['rms_00'])

#JASON2N
if 'JASON2N' in list_obs:
    df_count_JASON2N = pd.DataFrame(count[list_obs.index('JASON2N'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_JASON2N   = pd.DataFrame(omp[list_obs.index('JASON2N'), :, 0], index=dates, columns=['omp_00'])
    df_rms_JASON2N   = pd.DataFrame(rms[list_obs.index('JASON2N'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_JASON2N = pd.DataFrame(count_ref[list_obs.index('JASON2N'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_JASON2N   = pd.DataFrame(omp_ref[list_obs.index('JASON2N'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_JASON2N   = pd.DataFrame(rms_ref[list_obs.index('JASON2N'), :, 0], index=dates, columns=['rms_00'])

#HY2A
if 'HY2A' in list_obs:
    df_count_HY2A = pd.DataFrame(count[list_obs.index('HY2A'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_HY2A   = pd.DataFrame(omp[list_obs.index('HY2A'), :, 0], index=dates, columns=['omp_00'])
    df_rms_HY2A   = pd.DataFrame(rms[list_obs.index('HY2A'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_HY2A = pd.DataFrame(count_ref[list_obs.index('HY2A'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_HY2A   = pd.DataFrame(omp_ref[list_obs.index('HY2A'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_HY2A   = pd.DataFrame(rms_ref[list_obs.index('HY2A'), :, 0], index=dates, columns=['rms_00'])

#SENTINEL3A
if 'SENTINEL3A' in list_obs:
    df_count_S3A = pd.DataFrame(count[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_S3A   = pd.DataFrame(omp[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['omp_00'])
    df_rms_S3A   = pd.DataFrame(rms[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_S3A = pd.DataFrame(count_ref[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_S3A   = pd.DataFrame(omp_ref[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_S3A   = pd.DataFrame(rms_ref[list_obs.index('SENTINEL3A'), :, 0], index=dates, columns=['rms_00'])

#SENTINEL3B
if 'SENTINEL3B' in list_obs:
    df_count_S3B = pd.DataFrame(count[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_S3B   = pd.DataFrame(omp[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['omp_00'])
    df_rms_S3B   = pd.DataFrame(rms[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['rms_00'])
    df_count_ref_S3B = pd.DataFrame(count_ref[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['nobs_00'])
    df_omp_ref_S3B   = pd.DataFrame(omp_ref[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['omp_00'])
    df_rms_ref_S3B   = pd.DataFrame(rms_ref[list_obs.index('SENTINEL3B'), :, 0], index=dates, columns=['rms_00'])
#SST
if 'GEN_SST' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_SST['nobs_' + region] = pd.DataFrame(count[list_obs.index('GEN_SST'), :, k], index=dates)
        df_omp_SST['omp_' + region] = pd.DataFrame(omp[list_obs.index('GEN_SST'), :, k], index=dates)
        df_rms_SST['rms_' + region] = pd.DataFrame(rms[list_obs.index('GEN_SST'), :, k], index=dates)
        df_count_ref_SST['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('GEN_SST'), :, k], index=dates)
        df_omp_ref_SST['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('GEN_SST'), :, k], index=dates)
        df_rms_ref_SST['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('GEN_SST'), :, k], index=dates)

#SST_night
if 'GEN_SST_night' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_SST_night['nobs_' + region] = pd.DataFrame(count[list_obs.index('GEN_SST_night'), :, k], index=dates)
        df_omp_SST_night['omp_' + region] = pd.DataFrame(omp[list_obs.index('GEN_SST_night'), :, k], index=dates)
        df_rms_SST_night['rms_' + region] = pd.DataFrame(rms[list_obs.index('GEN_SST_night'), :, k], index=dates)
        df_count_ref_SST_night['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('GEN_SST_night'), :, k], index=dates)
        df_omp_ref_SST_night['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('GEN_SST_night'), :, k], index=dates)
        df_rms_ref_SST_night['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('GEN_SST_night'), :, k], index=dates)

#ALTIKA
if 'ALTIKA' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_ALTIKA['nobs_' + region] = pd.DataFrame(count[list_obs.index('ALTIKA'), :, k], index=dates)
        df_omp_ALTIKA['omp_' + region] = pd.DataFrame(omp[list_obs.index('ALTIKA'), :, k], index=dates)
        df_rms_ALTIKA['rms_' + region] = pd.DataFrame(rms[list_obs.index('ALTIKA'), :, k], index=dates)
        df_count_ref_ALTIKA['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('ALTIKA'), :, k], index=dates)
        df_omp_ref_ALTIKA['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('ALTIKA'), :, k], index=dates)
        df_rms_ref_ALTIKA['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('ALTIKA'), :, k], index=dates)

#JASON2
if 'JASON2' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_JASON2['nobs_' + region] = pd.DataFrame(count[list_obs.index('JASON2'), :, k], index=dates)
        df_omp_JASON2['omp_' + region] = pd.DataFrame(omp[list_obs.index('JASON2'), :, k], index=dates)
        df_rms_JASON2['rms_' + region] = pd.DataFrame(rms[list_obs.index('JASON2'), :, k], index=dates)
        df_count_ref_JASON2['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('JASON2'), :, k], index=dates)
        df_omp_ref_JASON2['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('JASON2'), :, k], index=dates)
        df_rms_ref_JASON2['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('JASON2'), :, k], index=dates)

#JASON3
if 'JASON3' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_JASON3['nobs_' + region] = pd.DataFrame(count[list_obs.index('JASON3'), :, k], index=dates)
        df_omp_JASON3['omp_' + region] = pd.DataFrame(omp[list_obs.index('JASON3'), :, k], index=dates)
        df_rms_JASON3['rms_' + region] = pd.DataFrame(rms[list_obs.index('JASON3'), :, k], index=dates)
        df_count_ref_JASON3['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('JASON3'), :, k], index=dates)
        df_omp_ref_JASON3['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('JASON3'), :, k], index=dates)
        df_rms_ref_JASON3['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('JASON3'), :, k], index=dates)

#JASON2N
if 'JASON2N' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_JASON2N['nobs_' + region] = pd.DataFrame(count[list_obs.index('JASON2N'), :, k], index=dates)
        df_omp_JASON2N['omp_' + region] = pd.DataFrame(omp[list_obs.index('JASON2N'), :, k], index=dates)
        df_rms_JASON2N['rms_' + region] = pd.DataFrame(rms[list_obs.index('JASON2N'), :, k], index=dates)
        df_count_ref_JASON2N['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('JASON2N'), :, k], index=dates)
        df_omp_ref_JASON2N['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('JASON2N'), :, k], index=dates)
        df_rms_ref_JASON2N['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('JASON2N'), :, k], index=dates)

#HY2A
if 'HY2A' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_HY2A['nobs_' + region] = pd.DataFrame(count[list_obs.index('HY2A'), :, k], index=dates)
        df_omp_HY2A['omp_' + region] = pd.DataFrame(omp[list_obs.index('HY2A'), :, k], index=dates)
        df_rms_HY2A['rms_' + region] = pd.DataFrame(rms[list_obs.index('HY2A'), :, k], index=dates)
        df_count_ref_HY2A['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('HY2A'), :, k], index=dates)
        df_omp_ref_HY2A['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('HY2A'), :, k], index=dates)
        df_rms_ref_HY2A['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('HY2A'), :, k], index=dates)

#CRYOSAT2
if 'CRYOSAT2' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_CRYOSAT2['nobs_' + region] = pd.DataFrame(count[list_obs.index('CRYOSAT2'), :, k], index=dates)
        df_omp_CRYOSAT2['omp_' + region] = pd.DataFrame(omp[list_obs.index('CRYOSAT2'), :, k], index=dates)
        df_rms_CRYOSAT2['rms_' + region] = pd.DataFrame(rms[list_obs.index('CRYOSAT2'), :, k], index=dates)
        df_count_ref_CRYOSAT2['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('CRYOSAT2'), :, k], index=dates)
        df_omp_ref_CRYOSAT2['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('CRYOSAT2'), :, k], index=dates)
        df_rms_ref_CRYOSAT2['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('CRYOSAT2'), :, k], index=dates)

#SENTINEL3A
if 'SENTINEL3A' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_S3A['nobs_' + region] = pd.DataFrame(count[list_obs.index('SENTINEL3A'), :, k], index=dates)
        df_omp_S3A['omp_' + region] = pd.DataFrame(omp[list_obs.index('SENTINEL3A'), :, k], index=dates)
        df_rms_S3A['rms_' + region] = pd.DataFrame(rms[list_obs.index('SENTINEL3A'), :, k], index=dates)
        df_count_ref_S3A['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('SENTINEL3A'), :, k], index=dates)
        df_omp_ref_S3A['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('SENTINEL3A'), :, k], index=dates)
        df_rms_ref_S3A['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('SENTINEL3A'), :, k], index=dates)

#SENTINEL3B
if 'SENTINEL3B' in list_obs:
    for region in region_num[1:]:
        k = int(region)
        df_count_S3B['nobs_' + region] = pd.DataFrame(count[list_obs.index('SENTINEL3B'), :, k], index=dates)
        df_omp_S3B['omp_' + region] = pd.DataFrame(omp[list_obs.index('SENTINEL3B'), :, k], index=dates)
        df_rms_S3B['rms_' + region] = pd.DataFrame(rms[list_obs.index('SENTINEL3B'), :, k], index=dates)
        df_count_ref_S3B['nobs_' + region] = pd.DataFrame(count_ref[list_obs.index('SENTINEL3B'), :, k], index=dates)
        df_omp_ref_S3B['omp_' + region] = pd.DataFrame(omp_ref[list_obs.index('SENTINEL3B'), :, k], index=dates)
        df_rms_ref_S3B['rms_' + region] = pd.DataFrame(rms_ref[list_obs.index('SENTINEL3B'), :, k], index=dates)

# Concatenate dataframes
if 'GEN_SST' in list_obs:
    df_SST     = pd.concat([df_count_SST, df_omp_SST, df_rms_SST], axis=1)
    df_ref_SST = pd.concat([df_count_ref_SST, df_omp_ref_SST, df_rms_ref_SST], axis=1)
if 'GEN_SST_night' in list_obs:
    df_SST_night     = pd.concat([df_count_SST_night, df_omp_SST_night, df_rms_SST_night], axis=1)
    df_ref_SST_night = pd.concat([df_count_ref_SST_night, df_omp_ref_SST_night, df_rms_ref_SST_night], axis=1)
if 'ALTIKA' in list_obs:
    df_ALTIKA  = pd.concat([df_count_ALTIKA, df_omp_ALTIKA, df_rms_ALTIKA], axis=1)
    df_ref_ALTIKA  = pd.concat([df_count_ref_ALTIKA, df_omp_ref_ALTIKA, df_rms_ref_ALTIKA], axis=1)
if 'JASON2' in list_obs:
    df_JASON2  = pd.concat([df_count_JASON2, df_omp_JASON2, df_rms_JASON2], axis=1)
    df_ref_JASON2  = pd.concat([df_count_ref_JASON2, df_omp_ref_JASON2, df_rms_ref_JASON2], axis=1)
if 'JASON3' in list_obs:
    df_JASON3  = pd.concat([df_count_JASON3, df_omp_JASON3, df_rms_JASON3], axis=1)
    df_ref_JASON3  = pd.concat([df_count_ref_JASON3, df_omp_ref_JASON3, df_rms_ref_JASON3], axis=1)
if 'JASON2N' in list_obs:
    df_JASON2N  = pd.concat([df_count_JASON2N, df_omp_JASON2N, df_rms_JASON2N], axis=1)
    df_ref_JASON2N  = pd.concat([df_count_ref_JASON2N, df_omp_ref_JASON2N, df_rms_ref_JASON2N], axis=1)
if 'CRYOSAT2' in list_obs:
    df_CRYOSAT2  = pd.concat([df_count_CRYOSAT2, df_omp_CRYOSAT2, df_rms_CRYOSAT2], axis=1)
    df_ref_CRYOSAT2  = pd.concat([df_count_ref_CRYOSAT2, df_omp_ref_CRYOSAT2, df_rms_ref_CRYOSAT2], axis=1)
if 'HY2A' in list_obs:
    df_HY2A  = pd.concat([df_count_HY2A, df_omp_HY2A, df_rms_HY2A], axis=1)
    df_ref_HY2A  = pd.concat([df_count_ref_HY2A, df_omp_ref_HY2A, df_rms_ref_HY2A], axis=1)
if 'SENTINEL3A' in list_obs:
    df_S3A  = pd.concat([df_count_S3A, df_omp_S3A, df_rms_S3A], axis=1)
    df_ref_S3A  = pd.concat([df_count_ref_S3A, df_omp_ref_S3A, df_rms_ref_S3A], axis=1)
if 'SENTINEL3B' in list_obs:
    df_S3B  = pd.concat([df_count_S3B, df_omp_S3B, df_rms_S3B], axis=1)
    df_ref_S3B  = pd.concat([df_count_ref_S3B, df_omp_ref_S3B, df_rms_ref_S3B], axis=1)



# Filter dates with zero data number and average
if 'GEN_SST' in list_obs:
    df_SST_m = filter_zeros_avg(df_SST)
    df_ref_SST_m = filter_zeros_avg(df_ref_SST)
if 'GEN_SST_night' in list_obs:
    df_SST_night_m = filter_zeros_avg(df_SST_night)
    df_ref_SST_night_m = filter_zeros_avg(df_ref_SST_night)
if 'ALTIKA' in list_obs:
    df_ALTIKA_m = filter_zeros_avg(df_ALTIKA)
    df_ref_ALTIKA_m = filter_zeros_avg(df_ref_ALTIKA)
if 'JASON2' in list_obs:
    df_JASON2_m = filter_zeros_avg(df_JASON2)
    df_ref_JASON2_m = filter_zeros_avg(df_ref_JASON2)
if 'JASON3' in list_obs:
    df_JASON3_m = filter_zeros_avg(df_JASON3)
    df_ref_JASON3_m = filter_zeros_avg(df_ref_JASON3)
if 'JASON2N' in list_obs:
    df_JASON2N_m = filter_zeros_avg(df_JASON2N)
    df_ref_JASON2N_m = filter_zeros_avg(df_ref_JASON2N)
if 'CRYOSAT2' in list_obs:
    df_CRYOSAT2_m = filter_zeros_avg(df_CRYOSAT2)
    df_ref_CRYOSAT2_m = filter_zeros_avg(df_ref_CRYOSAT2)
if 'HY2A' in list_obs:
    df_HY2A_m = filter_zeros_avg(df_HY2A)
    df_ref_HY2A_m = filter_zeros_avg(df_ref_HY2A)
if 'SENTINEL3A' in list_obs:
    df_S3A_m = filter_zeros_avg(df_S3A)
    df_ref_S3A_m = filter_zeros_avg(df_ref_S3A)
if 'SENTINEL3B' in list_obs:
    df_S3B_m = filter_zeros_avg(df_S3B)
    df_ref_S3B_m = filter_zeros_avg(df_ref_S3B)

# Figures production
print 'Figures production ...'
label_cycle = suite
label_ref = ref_suite

for reg in region_num:
    if 'GEN_SST' in list_obs:
        plot_timeseries(reg, df_SST, df_ref_SST, 'GEN_SST', label_cycle, label_ref)
    if 'GEN_SST_night' in list_obs:
        plot_timeseries(reg, df_SST_night, df_ref_SST_night, 'GEN_SST_night', label_cycle, label_ref)
    if 'ALTIKA' in list_obs:
        plot_timeseries(reg, df_ALTIKA, df_ref_ALTIKA, 'ALTIKA', label_cycle, label_ref)
    if 'JASON2' in list_obs:
        plot_timeseries(reg, df_JASON2, df_ref_JASON2, 'JASON2', label_cycle, label_ref)
    if 'JASON3' in list_obs:
        plot_timeseries(reg, df_JASON3, df_ref_JASON3, 'JASON3', label_cycle, label_ref)
    if 'JASON2N' in list_obs:
        plot_timeseries(reg, df_JASON2N, df_ref_JASON2N, 'JASON2N', label_cycle, label_ref)
    if 'CRYOSAT2' in list_obs:
        plot_timeseries(reg, df_CRYOSAT2, df_ref_CRYOSAT2, 'CRYOSAT2', label_cycle, label_ref)
    if 'HY2A' in list_obs:
        plot_timeseries(reg, df_HY2A, df_ref_HY2A, 'HY2A', label_cycle, label_ref)
    if 'SENTINEL3A' in list_obs:
        plot_timeseries(reg, df_S3A, df_ref_S3A, 'SENTINEL3A', label_cycle, label_ref)
    if 'SENTINEL3B' in list_obs:
        plot_timeseries(reg, df_S3B, df_ref_S3B, 'SENTINEL3B', label_cycle, label_ref)


k1 = len(regions)
k2 = k1 * 2
# Student t-test (only for RMS)
if 'GEN_SST' in list_obs:
    t_SST = np.zeros(k1)
    p_SST = np.zeros(k1)
if 'GEN_SST_night' in list_obs:
    t_SST_night = np.zeros(k1)
    p_SST_night = np.zeros(k1)
if 'ALTIKA' in list_obs:
    t_ALTIKA = np.zeros(k1)
    p_ALTIKA = np.zeros(k1)
if 'JASON2' in list_obs:
    t_JASON2 = np.zeros(k1)
    p_JASON2 = np.zeros(k1)
if 'JASON3' in list_obs:
    t_JASON3 = np.zeros(k1)
    p_JASON3 = np.zeros(k1)
if 'JASON2N' in list_obs:
    t_JASON2N = np.zeros(k1)
    p_JASON2N = np.zeros(k1)
if 'CRYOSAT2' in list_obs:
    t_CRYOSAT2 = np.zeros(k1)
    p_CRYOSAT2 = np.zeros(k1)
if 'HY2A' in list_obs:
    t_HY2A = np.zeros(k1)
    p_HY2A = np.zeros(k1)
if 'SENTINEL3A' in list_obs:
    t_S3A = np.zeros(k1)
    p_S3A = np.zeros(k1)
if 'SENTINEL3B' in list_obs:
    t_S3B = np.zeros(k1)
    p_S3B = np.zeros(k1)

for i in range(k2, len(df_SST.columns)):
    if 'GEN_SST' in list_obs:
        t_SST[i-k2], p_SST[i-k2] = stats.ttest_ind(df_SST.values[:, i], df_ref_SST.values[:, i])
    if 'GEN_SST_night' in list_obs:
        t_SST_night[i-k2], p_SST_night[i-k2] = stats.ttest_ind(df_SST_night.values[:, i], df_ref_SST_night.values[:, i])
    if 'ALTIKA' in list_obs:
        t_ALTIKA[i-k2], p_ALTIKA[i-k2] = stats.ttest_ind(df_ALTIKA.values[:, i], df_ref_ALTIKA.values[:, i])
    if 'JASON2' in list_obs:
        t_JASON2[i-k2], p_JASON2[i-k2] = stats.ttest_ind(df_JASON2.values[:, i], df_ref_JASON2.values[:, i])
    if 'JASON3' in list_obs:
        t_JASON3[i-k2], p_JASON3[i-k2] = stats.ttest_ind(df_JASON3.values[:, i], df_ref_JASON3.values[:, i])
    if 'JASON2N' in list_obs:
        t_JASON2N[i-k2], p_JASON2N[i-k2] = stats.ttest_ind(df_JASON2N.values[:, i], df_ref_JASON2N.values[:, i])
    if 'CRYOSAT2' in list_obs:
        t_CRYOSAT2[i-k2], p_CRYOSAT2[i-k2] = stats.ttest_ind(df_CRYOSAT2.values[:, i], df_ref_CRYOSAT2.values[:, i])
    if 'HY2A' in list_obs:
        t_HY2A[i-k2], p_HY2A[i-k2] = stats.ttest_ind(df_HY2A.values[:, i], df_ref_HY2A.values[:, i])
    if 'SENTINEL3A' in list_obs:
        t_S3A[i-k2], p_S3A[i-k2] = stats.ttest_ind(df_S3A.values[:, i], df_ref_S3A.values[:, i])
    if 'SENTINEL3B' in list_obs:
        t_S3B[i-k2], p_S3B[i-k2] = stats.ttest_ind(df_S3B.values[:, i], df_ref_S3B.values[:, i])


# Mean values figures (horizontal bars figures)

if 'GEN_SST' in list_obs:
    plot_mean_stat(df_SST_m, df_ref_SST_m, 'GEN_SST', suite, ref_suite, p_SST)
if 'GEN_SST_night' in list_obs:
    plot_mean_stat(df_SST_night_m, df_ref_SST_night_m, 'GEN_SST_night', suite, ref_suite, p_SST_night)
if 'ALTIKA' in list_obs:
    plot_mean_stat(df_ALTIKA_m, df_ref_ALTIKA_m, 'ALTIKA', suite, ref_suite, p_ALTIKA)
if 'JASON2' in list_obs:
    plot_mean_stat(df_JASON2_m, df_ref_JASON2_m, 'JASON2', suite, ref_suite, p_JASON2)
if 'JASON3' in list_obs:
    plot_mean_stat(df_JASON3_m, df_ref_JASON3_m, 'JASON3', suite, ref_suite, p_JASON3)
if 'JASON2N' in list_obs:
    plot_mean_stat(df_JASON2N_m, df_ref_JASON2N_m, 'JASON2N', suite, ref_suite, p_JASON2N)
if 'CRYOSAT2' in list_obs:
    plot_mean_stat(df_CRYOSAT2_m, df_ref_CRYOSAT2_m, 'CRYOSAT2', suite, ref_suite, p_CRYOSAT2)
if 'HY2A' in list_obs:
    plot_mean_stat(df_HY2A_m, df_ref_HY2A_m, 'HY2A', suite, ref_suite, p_HY2A)
if 'SENTINEL3A' in list_obs:
    plot_mean_stat(df_S3A_m, df_ref_S3A_m, 'SENTINEL3A', suite, ref_suite, p_S3A)
if 'SENTINEL3B' in list_obs:
    plot_mean_stat(df_S3B_m, df_ref_S3B_m, 'SENTINEL3B', suite, ref_suite, p_S3B)


print 'Finished in ... ', time.time() - initial_time, ' secondes'
