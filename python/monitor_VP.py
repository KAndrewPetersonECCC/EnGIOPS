import os
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
from importlib import reload

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import time

import read_qcola
import create_dates

dddir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/SAM2V2'
#file=ddir+'/gx_EE1.0/SAM2/002/20200115/DIAG/iau/20200115000_QCOLA_VP_BEST.nc'
#os.path.isfile(file)

date_range=[20200101, 20200520]
dates=create_dates.create_dates(date_range[0], date_range[1], 7)

expt='gx_EE1.0'

def global_mean_profile(expt, date_range, ddir=dddir, ref='gx4_a3.1', rdir='kch001',
                        trial='iau', group='VP/VP_GEN_PR_PF', ensemble=list(range(1,21)), 
                        plotto='GNU_PLOTS/'):


    time0 = time.time()
    ENT = read_qcola.read_VPOLA_ens(date_range, expt, ddir=ddir, trial=trial, group=group, ensemble=ensemble)

    VPC = read_qcola.read_VPOLA_dates(date_range, ref, ddir=rdir, trial=trial, group=group, ens=None)
    VPT = xr.concat(ENT, dim='edim')

    time1 = time.time()
    print( "TIME ELAPSED TO READ", time1 - time0)

    VPE = read_qcola.calc_EM_add_variance(VPT)
    VPC = read_qcola.add_square_error(VPC)
    VPE = read_qcola.add_square_error(VPE)

    time2 = time.time()
    print("TIME ELAPSED TO CALC EM ADD SQUARE ERRRORS", time2-time1, time2-time0)

    VPg = VPC.mean(dim='datanumber').compute()
    VPG = VPE.mean(dim='datanumber').compute()

    time3 = time.time()
    print("TIME ELAPSED TO COMPUTE GLOBAL", time3-time2, time3-time0)

    plot_profile(VPG, VPg, plotto=plotto)

    return

def global_mean_profile2(expt, date_range, ddir=dddir, ref='gx4_a3.1', rdir='kch001',
                        trial='iau', group='VP/VP_GEN_PR_PF', ensemble=list(range(1,21)), 
                        plotto='GNU_PLOTS/'):

    dates = create_dates.create_dates(date_range[0], date_range[1], 7)
    time0 = time.time()
    GLL = []
    for date in dates:
        ENS = read_qcola.read_VPOLA_ens([date], expt, ddir=ddir, trial=trial, group=group, ensemble=ensemble)
        VPe = xr.concat(ENS, dim='ensemble')
        VPm = read_qcola.calc_EM_add_variance(VPe)
        VPm = read_qcola.add_square_error(VPm)
        VPgg = VPm.mean(dim='datanumber').compute()
        GLL.append(VPgg)

    VPGT = xr.concat(GLL, dim='time')
    VPG = VPGT.mean(dim='time')

    VPC = read_qcola.read_VPOLA_dates(date_range, ref, ddir=rdir, trial=trial, group=group, ens=None)
    VPC = read_qcola.add_square_error(VPC)
    VPg = VPC.mean(dim='datanumber').compute()
    
    time1 = time.time()
    print( "TIME ELAPSED TO CALC", time1 - time0)

    plot_profile(VPG, VPg, plotto=plotto)
    
    return

def plot_profile(VPG, VPg, plotto="GNU_PLOTS/"):

    for V in ['T', 'S']:
        if ( V == 'T' ):var = 'temperature'
        if ( V == 'S' ):var = 'salinity'
        fig,axe = plt.subplots()
        axe.plot(np.sqrt(VPG['sqe_'+var]), VPG['dep_'+var], color='red', linestyle='-', label='ensemble')
        axe.plot(np.sqrt(VPg['sqe_'+var]), VPg['dep_'+var], color='blue', linestyle='-', label='deterministic')
        axe.plot(VPG['mis_'+var], VPG['dep_'+var], color='red', linestyle='--')
        axe.plot(VPg['mis_'+var], VPg['dep_'+var], color='blue', linestyle='--')
        axe.plot(np.sqrt(VPG['var_'+var]), VPG['dep_'+var], color='red', linestyle=':')
        axe.set_ylim(0, 500)
        axe.legend()
        axe.invert_yaxis()
        fig.savefig(plotto+V+'profile.png')
        plt.close(fig)

