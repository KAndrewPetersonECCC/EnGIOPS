# -*- coding: utf-8 -*-
# June 2020
import matplotlib
#matplotlib.use('Agg')

import numpy as np
from netCDF4 import Dataset as dt
import matplotlib.pyplot as plt
import cmocean as cmo
import GIOPS_map as gmap
import argparse
from datetime import date, timedelta, datetime
import pandas as pd

initial_time = datetime.now()
"""
ap = argparse.ArgumentParser()
ap.add_argument("--suite",       required=True, help="Experiment name")
ap.add_argument("--expdir",   required=True, help="Experiment path")
ap.add_argument("--outdir",  required=True, help="Output path")
#ap.add_argument("--start_date",  required=True, help="Start date")
ap.add_argument("--exp_date",  required=True, help="final date")
ap.add_argument("--cycle_",  required=True, help="ANAL or TRIAL")

suite_name   = ap.parse_args().suite
input_dir    = ap.parse_args().expdir
output_dir   = ap.parse_args().outdir
#sdate   = ap.parse_args().start_date
fdate   = ap.parse_args().exp_date
cycle = ap.parse_args().cycle_

"""


suite_name = 'GX_new_pstar_cstar'
input_dir = '/home/kch001/data_hall3/maestro_archives/GX_new_pstar_cstar/SAM2/20190313/DIA/'
#sdate='20190312'
fdate='20190313'
output_dir = '/home/aag000/data_hall3/giops_work/monitoring/'
cycle='TRIAL'


# Make sure paths end with /
if not input_dir.endswith('/'):
    input_dir = input_dir + '/'
if not output_dir.endswith('/'):
    output_dir = output_dir + '/'

run = suite_name

# make fdate one day before
fdate = datetime(year=int(fdate[0:4]),month=int(fdate[4:6]),day=int(fdate[6:8])) - timedelta(days=1)
fdate = str(fdate)[0:4]+str(fdate)[5:7]+str(fdate)[8:10]
# get date 6 days before
sdate = datetime(year=int(fdate[0:4]),month=int(fdate[4:6]),day=int(fdate[6:8])) - timedelta(days=6)
#convert sdate back to a string
sdate = str(sdate)[0:4]+str(sdate)[5:7]+str(sdate)[8:10]




def s2date(nbdays):
    # enter nb of days since 1950 01 01    
    start = date(1950,1,1)      
    delta = timedelta(nbdays)     
    offset = start + delta   
    return offset

fileu = input_dir + 'ORCA025-CMC-'+cycle.upper()+'_1d_gridU-RUN-crs_'+sdate+'-'+fdate+'.nc'
filev = input_dir + 'ORCA025-CMC-'+cycle.upper()+'_1d_gridV-RUN-crs_'+sdate+'-'+fdate+'.nc'
filet = input_dir + 'ORCA025-CMC-'+cycle.upper()+'_1d_gridT-RUN-crs_'+sdate+'-'+fdate+'.nc'

# load list_var
d = pd.read_csv('CRS_var.txt', delimiter=',', header=None)
list_var = []
for k in range(0,len(d)-1):

   if int(d[1][k]):
        list_var.append(d[0][k].strip(','))
print(list_var)

local_var_list = []

fid = dt(fileu)
dep = fid.variables['depthu'][:].squeeze()
#if ('UINST'in list_var) or ('speed' in list_var): UINST= fid.variables['UINST'][:].squeeze(); local_var_list.append('UINST') 
if ('TAUX'in list_var)  or ('TAU' in list_var)  : TAUX= fid.variables['TAUX'][:].squeeze(); local_var_list.append('TAUX')
time = fid.variables['time_counter'][:].squeeze()
fid.close()

#if 'speed'         in list_var: local_var_list.append('speed')
if 'TAU'         in list_var: local_var_list.append('TAU')

fid = dt(filev)
#depth = fid.variables['depthv'][:].squeeze()
#if ('VINST'in list_var) or ('speed' in list_var) : VINST= fid.variables['VINST'][:].squeeze(); local_var_list.append('VINST')
if ('TAUY'in list_var)  or ('TAU' in list_var)  : TAUY= fid.variables['TAUY'][:].squeeze(); local_var_list.append('TAUY')
fid.close()

fid = dt(filet)
# coords 
lon     = fid.variables['nav_lon'][:].squeeze()
lat     = fid.variables['nav_lat'][:].squeeze()
SINST     = fid.variables['SINST'][:].squeeze()
fid.close()

contmask = np.zeros(SINST.shape)
contmask[SINST==0]=1

#if 'speed'         in list_var:
#    speed = np.sqrt(UINST**2+VINST**2)
#speed = speed[:,0,:,:]
if 'TAU'         in list_var:
    TAU = np.sqrt(TAUX**2+TAUY**2)
#contmasku = np.zeros(U10m.shape)
#contmasku[U10m==0]=1
dates = [s2date((i/3600.)/24.) for i in time]


# depths
dd = pd.read_csv('depths.txt', delimiter='\n', header=None)
depths = []
for k in range(0,len(dd)):
        depths.append(float(dd[0][k].strip(',')))
print(depths)
#depths = [0.49402538, 92.326073, 318.12744, 541.08893, 902.33929, 1941.8934]


#Mask continents
# Dymamic, sea level variables
#if 'speed'         in list_var: speed[contmask==1] = np.nan; 
if 'TAU'           in list_var: TAU[contmask[:,0,:,:]==1] = np.nan; 
if 'TAUX'in list_var  : TAUX[contmask[:,0,:,:]==1] = np.nan; 
if 'TAUY'in list_var  : TAUY[contmask[:,0,:,:]==1] = np.nan; 




for d in dates:
        print(d)
        
        if 'TAU'         in list_var:
            # TAU
            fig = plt.figure(figsize = (6,8))
            ax = plt.gca()
            ax.set_facecolor('silver')
            #plt.title('Salinity \n depth: '+str(round(depth,2WARNING: No translation for (keysym 0x0, NoSymbol)ate[4:6]+'/'+date[6:8], size = 18 )
            ax1 = plt.subplot(111)
            plt.title(r'Wind Stress $(TAUX^2+TAUY^2)^{1/2}$'+'\n \n', size = 11 )
            plt.text(0,365,'  Run: ' + run, size = 10)
            plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
            plt.text(350,350,' date: ' + str(d), size = 10)
            gmap.map(TAU,r'$N/m^2$', np.linspace(0,2,5),dates.index(d),'rainbow',contmask[:,0,:,:],lon,lat)
            #plt.show()         
            plt.savefig(output_dir+str(d)[0:4]+str(d)[5:7]+str(d)[8:10]+'_TAU_'+cycle+'.png')
            plt.close()


        if 'TAUX'         in list_var:
            # TAUX
            fig = plt.figure(figsize = (6,8))
            ax = plt.gca()
            ax.set_facecolor('silver')
            #plt.title('Salinity \n depth: '+str(round(depth,2WARNING: No translation for (keysym 0x0, NoSymbol)ate[4:6]+'/'+date[6:8], size = 18 )
            ax1 = plt.subplot(111)
            plt.title(r'Zonal Wind Stress (TAUX)'+'\n \n', size = 11 )
            plt.text(0,365,'  Run: ' + run, size = 10)
            plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
            plt.text(350,350,' date: ' + str(d), size = 10)
            gmap.map(TAUX,r'$N/m^2$', np.linspace(-2,2,5),dates.index(d),cmo.cm.balance,contmask[:,0,:,:],lon,lat)
            #plt.show()         
            plt.savefig(output_dir+str(d)[0:4]+str(d)[5:7]+str(d)[8:10]+'_TAUX_'+cycle+'.png')
            plt.close()
        
        
        if 'TAUY'         in list_var:
            # TAUY
            fig = plt.figure(figsize = (6,8))
            ax = plt.gca()
            ax.set_facecolor('silver')
            ax1 = plt.subplot(111)
            plt.title(r'Meridional Wind Stress (TAUY)'+'\n \n', size = 11 )
            plt.text(0,365,'  Run: ' + run, size = 10)
            plt.text(0,350,'  Cycle: ' + cycle.upper(),size =10)
            plt.text(350,350,' date: ' + str(d), size = 10)
            gmap.map(TAUY,r'$N/m^2$', np.linspace(-2,2,5),dates.index(d),cmo.cm.balance,contmask[:,0,:,:],lon,lat)
            #plt.show()         
            plt.savefig(output_dir+str(d)[0:4]+str(d)[5:7]+str(d)[8:10]+'_TAUY_'+cycle+'.png')
            plt.close()
            
            
            
print('finished in ...' + str((datetime.now() - initial_time)))
