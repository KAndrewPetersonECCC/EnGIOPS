#! /usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import numpy as np
from netCDF4 import Dataset
import netCDF4
import matplotlib.pyplot as plt
import GIOPS_map as gmap
import argparse
from datetime import date, timedelta, datetime
import glob, os, sys
import gzip
import pandas as pd

"""
1) reads a list of variable to diagnose/ plot maps of called list_var
2) for the variables loaded in 1d_gridT files AND listed in list_var, 
a second list called local_var_list is created to lighten the script
"""
initial_time = datetime.now()

# Functions definition

def s2date(nbdays):
    # enter nb of days since 1950 01 01    
    start = date(1950,1,1)      
    delta = timedelta(nbdays)     
    offset = start + delta   
    return offset

ap = argparse.ArgumentParser()
ap.add_argument("--suite",       required=True, help="Experiment name")
ap.add_argument("--expdir",      required=True, help="Experiment path")
ap.add_argument("--outdir",      required=True, help="Output path")
ap.add_argument("--exp_date",    required=True, help="Experiment date")
ap.add_argument("--run_type",      required=True, help="ANAL or TRIAL")

suite_name   = ap.parse_args().suite
input_dir    = ap.parse_args().expdir
output_dir   = ap.parse_args().outdir
exp_date     = ap.parse_args().exp_date
cycle        = ap.parse_args().run_type

"""
suite_name = 'GX_new_pstar_cstar'
input_dir = '/home/kch001/data_hall3/maestro_archives/GX_new_pstar_cstar/SAM2/20190313/DIA/'
#sdate='20190312'
fdate='20190313'
output_dir = '/home/aag000/data_hall3/giops_work/monitoring/'
cycle='TRIAL'
"""

# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not output_dir.endswith('/'):
    output_dir = output_dir + '/'

# Dates definition
date_m0 = datetime.strptime(exp_date, "%Y%m%d")
date_m1 = date_m0 - timedelta(days=1)
date_m7 = date_m0 - timedelta(days=7)
date_p5 = date_m0 + timedelta(days=5)

str_date_title = datetime.strftime(date_m0, "%Y-%m-%d")
str_date_m1    = datetime.strftime(date_m1, "%Y%m%d")
str_date_m7    = datetime.strftime(date_m7, "%Y%m%d")
str_date_p5    = datetime.strftime(date_p5, "%Y%m%d")

run = suite_name

# load variable list
d = pd.read_csv('CRS_var.txt', delimiter=',', header=None)
list_var = []
for k in range(0,len(d)-1):
    if int(d[1][k]):
        list_var.append(d[0][k].strip(','))
print(list_var)

if cycle == 'ANAL':
    filename = input_dir + 'ORCA025-CMC-' + cycle.upper() + '_1d_gridT-RUN-crs_' + str_date_m1 + '-' + str_date_p5 + '.nc'
elif cycle =='TRIAL':
    filename = input_dir + 'ORCA025-CMC-' + cycle.upper() + '_1d_gridT-RUN-crs_' + str_date_m7 + '-' + str_date_m1 + '.nc'
else:
    sys.exit('Wrong cycle type. It should be ANAL or TRIAL ..')
    
fid = Dataset(filename)
# coords 
lon     = fid.variables['nav_lon'][:].squeeze()
lat     = fid.variables['nav_lat'][:].squeeze()
time_int= fid.variables['time_instant'][:].squeeze()
dep     = fid.variables['deptht'][:].squeeze()

# Build variables list
local_var_list =[]

# Surface Flux variables (thermo-dynamic)
# Surface rainfall flux kg/m2/s
if 'P' in list_var: 
    P = fid.variables['P'][:].squeeze()
    local_var_list.append('P') 

# Fresh water flux kg/m2/s
if 'EMP' in list_var: 
    EMP = fid.variables['EMP'][:].squeeze()
    local_var_list.append('EMP') 

# sensible_heat_flux_over_ocean W/m2
if 'QS' in list_var: 
    QS  = fid.variables['QS'][:].squeeze()
    local_var_list.append('QS') 

# latent_heat_flux_over_ocean W/m2
if 'QH' in list_var: 
    QH  = fid.variables['QH'][:].squeeze()
    local_var_list.append('QH') 

# infra_red_heat_flux_over_ocean W/m2
if 'QLW' in list_var: 
    QLW = fid.variables['QLW'][:].squeeze()
    local_var_list.append('QLW') 

# net_solar_flux_at_the_ocean_surface
if 'QSR' in list_var: 
    QSR = fid.variables['QSR'][:].squeeze()
    local_var_list.append('QSR') 

# net_downward_heat_flux
if 'Q' in list_var: 
    Q = fid.variables['Q'][:].squeeze()
    local_var_list.append('Q')

# Wind speed
if 'U10m' in list_var:
    U10m = fid.variables['U10m'][:].squeeze()
    local_var_list.append('U10m') 

# relative_humidity
if 'H2M' in list_var: 
    H2M = fid.variables['H2M'][:].squeeze()
    local_var_list.append('H2M')

# air_temperature
if 'TAIR' in list_var: 
    TAIR = fid.variables['TAIR'][:].squeeze()
    local_var_list.append('TAIR')

SINST  = fid.variables['SINST'][:].squeeze()
fid.close()


contmask = np.zeros(U10m.shape)
if cycle == 'ANAL':
    contmask[SINST[0,:,:]==0]=1
if cycle == 'TRIAL':
    contmask[SINST[:,0,:,:]==0]=1

dates = [s2date((i/3600.)/24.) for i in [time_int]]


# depths
dd = pd.read_csv('selected_depths.txt', delimiter='\n', header=None)
depths = []
for k in range(0,len(dd)):
        depths.append(float(dd[0][k].strip(',')))
print(depths)


#Mask continents
for var in local_var_list:
    exec(var+"[contmask==1]   = np.nan;")


for d in dates:
    str_d = datetime.strftime(d, "%Y%m%d")
    if 'U10m' in local_var_list:
        # U10m
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        gmap.map(U10m, r'm/s', np.arange(0, 32, 4), dates.index(d), 'rainbow', contmask, lon, lat)
        plt.title(r'Wind speed (U10m)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        plt.savefig(output_dir + str_d + '_U10m_' + cycle + '.png')
        plt.close()
        
    if 'EMP' in local_var_list:
        #EMP
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        gmap.map(EMP*10**4,r'$10^{-4} kg/m^2s$', np.arange(-5,5.1,2.5), dates.index(d), 'seismic', contmask, lon, lat)
        plt.title(r'Fresh water flux (EMP)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        plt.savefig(output_dir + str_d + '_EMP_' + cycle + '.png')
        plt.close()
        
    if 'P' in local_var_list:
        # P
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        gmap.map(P*10**9, r'$10^{-9} kg/m^2s$', np.linspace(0, 5.1, 5), dates.index(d), 'Blues', contmask, lon, lat)
        plt.title(r'Surface rainfall flux (P)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        plt.savefig(output_dir + str_d + '_P_' + cycle + '.png')
        plt.close()
     
    if 'QS' in local_var_list:
        # QS
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        plt.title(r' Sensible Heat Flux over Ocean (QS)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        gmap.map(QS, r'$W/m^2$', np.linspace(-200,200,11), dates.index(d), 'seismic', contmask, lon, lat)
        plt.savefig(output_dir+str_d + '_QS_' + cycle + '.png')       
        plt.close()
        
    if 'QLW' in local_var_list:
        # QLW
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        plt.title(r'Infra-red Heat Flux over Ocean (QLW)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        gmap.map(QLW,r'$W/m^2$', np.linspace(-200,200,11), dates.index(d), 'seismic', contmask, lon, lat)
        plt.savefig(output_dir + str_d + '_QLW_' + cycle + '.png')       
        plt.close()
            
    if 'QH' in local_var_list:
        # QH
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        plt.title(r'Latent Heat Flux over Ocean (QH)'+'\n \n', size = 14 )
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        gmap.map(QH, r'$W/m^2$', np.linspace(-300,300,11), dates.index(d), 'seismic', contmask, lon, lat)
        plt.savefig(output_dir + str_d + '_QH_' + cycle + '.png')       
        plt.close()
            
    if 'Q' in local_var_list:
        # Q
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        plt.title(r' net_downward_heat_flux (Q)'+'\n \n', size = 14 )
        gmap.map(Q,r'$W/m2$', np.arange(-500,500.1,100),dates.index(d),'seismic',contmask,lon,lat)
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        plt.savefig(output_dir + str_d + '_Q_' + cycle + '.png')
        plt.close()
            
        
    if 'QSR' in local_var_list:
        # QSR 
        fig = plt.figure(figsize = (8,6))
        fig.gca().set_facecolor('silver')
        plt.title(r'net_solar_flux_at_the_ocean_surface (QSR)'+'\n \n', size = 14 )
        gmap.map(QSR,r'$W/m2$', np.arange(0,140.1,20), dates.index(d), 'plasma', contmask,lon,lat)
        plt.text(0,365,'  Run: ' + run, size = 10)
        plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
        plt.text(350,350,' date: ' + str(d), size = 10)
        plt.savefig(output_dir + str_d + '_QSR_' + cycle + '.png')
        plt.close()

print('finished in ...' + str((datetime.now() - initial_time)))
