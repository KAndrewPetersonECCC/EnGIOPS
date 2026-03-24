import os
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
from importlib import reload

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import time
from multiprocessing import Pool
from itertools import repeat

import read_qcola
import create_dates

def plot_profile(VP_CORA, VP_EN4, ext=['', '_CORA'], plotto="GNU_PLOTS/"):
    
    pext = "".join(ext)
    for V in ['T', 'S']:
        if ( V == 'T' ):var = 'temperature'
        if ( V == 'S' ):var = 'salinity'
        fig,axe = plt.subplots()
        axe.plot(np.sqrt(VP_CORA['sqe_'+var+ext[0]]), VP_CORA['dep_'+var], color='blue', linestyle='-', label='CORA')
        axe.plot(np.sqrt(VP_EN4['sqe_'+var+ext[1]]), VP_EN4['dep_'+var], color='red', linestyle='-', label='EN4')
        axe.plot(VP_CORA['mis_'+var+ext[0]], VP_CORA['dep_'+var], color='blue', linestyle='--')
        axe.plot(VP_EN4['mis_'+var+ext[1]], VP_EN4['dep_'+var], color='red', linestyle='--')
        axe.set_ylim(0, 500)
        axe.legend()
        axe.invert_yaxis()
        axe.set_title('Global Misfit wrt '+pext[1:])
        fig.savefig(plotto+V+pext+'profile.png')
        plt.close(fig)

    
def find_point_in_xarray(VP, VP_ref, ii):
    time, lat, lon = [VP_ref.isel(datanumber=ii)[var] for var in ['time', 'latitude', 'longitude']]
    II = np.where( (VP['time'] == time) & (VP['latitude'] == lat) & (VP['longitude'] == lon) )
    if ( len(II[0]) == 0 ): print('missing', ii)
    if ( len(II[0]) > 1 ): print('duplicate', ii, II)
    return VP.sel(datanumber=list(II[0]) )
    
num_cpus = len(os.sched_getaffinity(0))
def subset_to_reference(VP, VP_ref):
    nd = len(VP_ref['time'])
    VP_NEW = []
    for ii in range(nd):
        VP_NEW.append(find_point_in_xarray(VP, VP_ref, ii))
    VP_NEW = xr.concat(VP_NEW, dim='datanumber')
    return VP_NEW
    
def subset_to_reference_mp(VP, VP_ref):  
    nd = len(VP_ref['time'])
    nproc = min([num_cpus, nd])
    ThePool = Pool(nproc)
    izip = list( zip(repeat(VP.compute()), repeat(VP_ref.compute()), list(range(len(VP_ref['time']))) ) )
    VP_NEW = ThePool.starmap(find_point_in_xarray, izip)
    ThePool.close()
    ThePool.join()
    VP_NEW = xr.concat(VP_NEW, dim='datanumber')
    return VP_NEW

def subset_to_reference_list(VP_list, VP_ref):
    nproc = min([num_cpus, len(VP_list) ])
    ThePool = Pool(nproc)
    izip = [ [ VP.compute(), VP_ref.compute() ] for VP in VP_list]
    VP_LIST = ThePool.starmap(subset_to_reference, izip)
    ThePool.close()
    ThePool.join()
    return VP_LIST
    
def subset_to_reference_liss(VP_list, VP_ref):
    VP_LIST = []
    VP_LIST = [ subset_to_reference_mp(VP, VP_ref) for VP in VP_list ]
    return VP_LIST    

def find_duplicates(VP):
    duplicate = []
    for ii in range(len(VP['time'])):
        time, lat, lon = [VP.isel(datanumber=ii)[var] for var in ['time', 'latitude', 'longitude']]
        II = np.where( (VP['time'] == time) & (VP['latitude'] == lat) & (VP['longitude'] == lon) )
        if ( len(II[0]) == 0 ): print('missing', ii)
        if ( len(II[0]) > 1 ): print('duplicate', ii, II)
        if ( len(II[0]) > 1 ): duplicate.append(II)
    return duplicate
    
def find_duplicates_to_index(ii, VP):
   time, lat, lon = [VP.isel(datanumber=ii)[var] for var in ['time', 'latitude', 'longitude']] 
   II = np.where( (VP['time'] == time) & (VP['latitude'] == lat) & (VP['longitude'] == lon) )
   return list(II[0])

def find_duplicates_mp(VP):
    nd = len(VP['time'])
    nproc = min([num_cpus, nd])
    ThePool = Pool(nproc)
    izip = list( zip( list(range(nd)), repeat(VP.compute()) ) )
    DUPL = ThePool.starmap(find_duplicates_to_index, izip)
    ThePool.close()
    ThePool.join()
    return DUPL

   
def remove_duplicates(VP):
    duplicate = []
    VP_NEW = []
    for ii in range(len(VP['time'])):
        time, lat, lon = [VP.isel(datanumber=ii)[var] for var in ['time', 'latitude', 'longitude']]
        II = np.where( (VP['time'] == time) & (VP['latitude'] == lat) & (VP['longitude'] == lon) )
        if ( len(II[0]) > 1 ): print('duplicate', ii, II[0])
        if ( ii not in duplicate):
          VP_NEW.append(VP.isel(datanumber=list(II[0])).mean(dim='datanumber') )
        if ( len(II[0]) > 1 ): duplicate.extend(II[0])
    VP_NEW = xr.concat(VP_NEW, dim='datanumber')
    return VP_NEW
    
def remove_duplicates_mp(VP):
    DUPL = find_duplicates_mp(VP)
    duplicate = []
    VP_NEW = []
    for ii, dupl in enumerate(DUPL):
        #if ( len(dupl) > 1 ): print('duplicate', ii, dupl)
        if ( ii not in duplicate):
          VP_NEW.append(VP.isel(datanumber=dupl).mean(dim='datanumber') )
        if ( len(dupl) > 1 ): duplicate.extend(dupl)
    VP_NEW = xr.concat(VP_NEW, dim='datanumber')
    return VP_NEW
    
if ( __name__ == '__main__' ):

    date_range = [20190925, 20200923]
    dates = create_dates.create_dates(date_range[0], date_range[1], 7)
    group = 'VP/VP_GEN_PR_PF'
    expt_cora = 'reanalyse'
    expt_EN4 = 'reanalyse_EN4'


    #VP_CORA = read_qcola.read_VPOLA_dates(date_range, expt_cora, ddir='rrh002', trial='iau', group=group, ens=None)
    #VP_EN4 = read_qcola.read_VPOLA_dates(date_range, expt_EN4, ddir='rrh002', trial='iau', group=group, ens=None)

    # BECAUSE THERE IS ONE OCCURENCE WHEN EN4 has more observations to CORA best to do by date
    VP_CORA = []
    VP_EN4 = []
    for date in dates:
        VPR = read_qcola.read_VPOLA_dates([date], expt_cora, ddir='rrh002', trial='iau', group=group, ens=None)
        VP = read_qcola.read_VPOLA_dates([date], expt_EN4, ddir='rrh002', trial='iau', group=group, ens=None)
        ndR = len(VPR['time'])
        nd = len(VP['time'])
        if ( ndR < nd ):
            print(date, ndR, nd)
            VP = subset_to_reference_mp(VP, VPR)
        VP_CORA.append(VPR)
        VP_EN4.append(VP)

    VP_CORA = xr.concat(VP_CORA, dim='datanumber')
    VP_EN4 = xr.concat(VP_EN4, dim='datanumber')

    VP_CORA['mis_temperature_EN4'] = VP_EN4['obs_temperature'] - VP_CORA['eqv_temperature']
    VP_EN4['mis_temperature_CORA'] = VP_CORA['obs_temperature'] - VP_EN4['eqv_temperature']
    VP_CORA['mis_salinity_EN4'] = VP_EN4['obs_salinity'] - VP_CORA['eqv_salinity']
    VP_EN4['mis_salinity_CORA'] = VP_CORA['obs_salinity'] - VP_EN4['eqv_salinity']

    VP_CORA['sqe_temperature'] = np.square(VP_CORA['mis_temperature'])
    VP_CORA['sqe_temperature_EN4'] = np.square(VP_CORA['mis_temperature_EN4'])
    VP_CORA['sqe_salinity'] = np.square(VP_CORA['mis_salinity'])
    VP_CORA['sqe_salinity_EN4'] = np.square(VP_CORA['mis_salinity_EN4'])

    VP_EN4['sqe_temperature'] = np.square(VP_EN4['mis_temperature'])
    VP_EN4['sqe_temperature_CORA'] = np.square(VP_EN4['mis_temperature_CORA'])
    VP_EN4['sqe_salinity'] = np.square(VP_EN4['mis_salinity'])
    VP_EN4['sqe_salinity_CORA'] = np.square(VP_EN4['mis_salinity_CORA'])

    # GLOBAL MEANS
    VPG_CORA = VP_CORA.mean(dim='datanumber')
    VPG_EN4 = VP_EN4.mean(dim='datanumber')


    plot_profile(VPG_CORA, VPG_EN4, ext=['', '_CORA'], plotto='REN4_PLOTS/')
    plot_profile(VPG_CORA, VPG_EN4, ext=['_EN4', ''], plotto='REN4_PLOTS/')

