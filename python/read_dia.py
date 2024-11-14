
import sys
import subprocess
this_dir='/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python'
sys.path.insert(0, this_dir)
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import pytz
import os.path
import netCDF4
import scipy.interpolate
import glob

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

import read_grid
import isoheatcontent
import cplot
#import find_hall
import area_wgt_average
import datadatefile
import write_nc_grid

TOPDIR='/home/dpe000/EnGIOPS'
#hall = find_hall.find_hall()
nensembles=21
default_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0/SAM2/20211229/DIA/ORCA025-CMC-ANAL_1d_grid_T_2021122900.nc'
mask = read_grid.read_mask(var='tmask')
maskt = read_grid.read_mask(var='tmask')
masku = read_grid.read_mask(var='umask')
maskv = read_grid.read_mask(var='vmask')
e3t = read_grid.read_e3t_mesh(var='e3t_0')
e3u = read_grid.read_e3t_mesh(var='e3u_0')
e3v = read_grid.read_e3t_mesh(var='e3v_0')
e1t = read_grid.read_mesh_var('e1t')
e2t = read_grid.read_mesh_var('e2t')
e1u = read_grid.read_mesh_var('e1u')
e2u = read_grid.read_mesh_var('e2u')
e1v = read_grid.read_mesh_var('e1v')
e2v = read_grid.read_mesh_var('e2v')
nav_lon, nav_lat, nav_area = read_grid.read_coord()

SH_COMMS = { 
             "PLOTS" : "/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh",
             "RATIO" : "/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_ratios.sh"
           }

ENSEMBLES = { 20 : np.arange(21),
              21 : np.arange(21),
               6 : np.arange(7),
               7 : np.arange(7)
            }
            
def get_COMMAND(key):
    if ( key == 'keys' ): return SH_COMMS.keys()
    return SH_COMMS[key]           
def get_ENSEMBLE(key):
    if ( key == 'keys' ): return ENSEMBLES.keys()
    return ENSEMBLES[key]           

def loop_dates_with_command(date_range, command=SH_COMMS["PLOTS"], expts='GIOPS_T', pdirs='PFIG', ensemble=ENSEMBLES[21], dry_run=False ):
    bash='bash'
    if ( dry_run ): bash='echo'
    date_start = date_range[0]
    date_final = date_range[1]
    date_incre = 7
    if ( len(date_range) > 2 ): date_incre = date_range[2]
    if ( ( isinstance(date_start, int) ) or ( isinstance(date_start, str) ) ): date_start = datadatefile.convert_strint_date(date_start)
    if ( ( isinstance(date_final, int) ) or ( isinstance(date_final, str) ) ): date_final = datadatefile.convert_strint_date(date_final)
    date=date_start

    if ( isinstance(expts, str ) ): expts=[expts]
    if ( isinstance(pdirs, str ) ): pdirs=[pdirs]
    if ( isinstance(ensemble, str) ): 
        ensemble_str = ensemble
    else:
        ensemble_str=str(ensemble)[1:-1]  # removes []
    
    while ( date <= date_final ):
        datestr, dateint=datadatefile.convert_date_strint(date)
        for iexpt, expt in enumerate(expts):
            pdir=pdirs[iexpt]
            call_list=[bash, command, '-d='+datestr, '-x='+expt, '-p='+pdir, '-e='+ensemble_str]
            print(' '.join(call_list))
            subprocess.call(call_list)
        date=date+datetime.timedelta(days=7)
    return

def read_sam2_times(file=default_file, fld='time_counter', T_ref=datetime.datetime(1950,1,1, 0,0,0,0, pytz.UTC)):
    dataset = netCDF4.Dataset(file)
    Tsec = dataset.variables[fld][:].astype(int)
    Timestamp = []
    for tsec in Tsec:
        Timestamp.append(T_ref + datetime.timedelta(seconds=int(tsec)))
    dataset.close()
    return Timestamp
               
def read_sam2_levels(file=default_file, fld='deptht'):
    dataset = netCDF4.Dataset(file)
    depth = dataset.variables[fld][:]
    dataset.close()
    return depth
               
def read_sam2_grid(file, fld='thetao'):
    dataset = netCDF4.Dataset(file)
    TM=dataset.variables[fld][:]
    lat=dataset.variables['nav_lat'][:]
    lon=dataset.variables['nav_lon'][:]
    #
    # NEED TO TRANSPOSE TO FIT Standard File Standard of (x,y)
    if ( TM.ndim == 4 ): TM=np.transpose(TM, (0, 1, 3, 2))
    if ( TM.ndim == 3 ): TM=np.transpose(TM, (0, 2, 1))
    if ( TM.ndim == 2 ): TM=np.transpose(TM, (1, 0))

    lat=np.transpose(lat)
    lon=np.transpose(lon)
    
    dataset.close()
    
    return lon, lat, TM
    
def read_sam2_grid_t(file):
    lon, lat, TM = read_sam2_grid(file,'thetao')
    __, __, SALW = read_sam2_grid(file, 'so')
    return lon, lat, TM, SALW

filu='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_U_2020110400.nc'
filv='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_V_2020110400.nc'
filh='fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1h_grid_T_2D_2020110400.nc'

def read_sam2_grid_u(filu):
    lonu, latu, UO = read_sam2_grid(filu, 'uo')
    return lonu, latu, UO

def read_sam2_grid_v(filv):
    lonv, latv, VO = read_sam2_grid(filu, 'vo')
    return lonv, latv, VO

def regrid_UtoT(Uo):
    nt=1
    nz=1
    if ( Uo.ndim == 4 ): nt, nz, nx, ny = Uo.shape
    if ( Uo.ndim == 3 ): nz, nx, ny = Uo.shape
    if ( Uo.ndim == 2 ): nx, ny = Uo.shape
    U4 = np.reshape(Uo, (nt,nz,nx,ny))
    
    UT = np.zeros((nt, nz, nx, ny))

    UT[:,:,0,:] = 0.5 * ( U4[:,:,0,:] + U4[:,:,-3,:] ) 
    for ix in range(1,nx):
        UT[:,:,ix,:] = 0.5 * ( U4[:,:,ix,:] + U4[:,:,ix-1,:] )
    
    if ( Uo.ndim == 3 ): UT = np.reshape(UT, [nz, nx, ny])
    if ( Uo.ndim == 2 ): UT = np.reshape(UT, [nx, ny])
    
    return UT
        
def regrid_VtoT(Vo):
    nt=1
    nz=1
    if ( Vo.ndim == 4 ): nt, nz, nx, ny = Vo.shape
    if ( Vo.ndim == 3 ): nz, nx, ny = Vo.shape
    if ( Vo.ndim == 2 ): nx, ny = Vo.shape
    V4 = np.reshape(Vo, (nt,nz,nx,ny))
    
    VT = np.zeros((nt, nz, nx, ny))
    VT[:,:,:,0] = 0.0
    for iy in range(1,ny):
        VT[:,:,:,iy] = 0.5 * ( V4[:,:,:,iy] + V4[:,:,:,iy-1] )
    
    if ( Vo.ndim == 3 ): VT = np.reshape(VT, [nz, nx, ny])
    if ( Vo.ndim == 2 ): VT = np.reshape(VT, [nx, ny])
    
    return VT
    
    
def regrid_to_T(lonlat,Utuple):
   (lon,lat) = lonlat
   lonu, latu, U0 = Utuple
   nt=1
   nz=1
   if ( U0.ndim == 4 ): nt, nz, nx, ny = U0.shape
   if ( U0.ndim == 3 ): nz, nx, ny = U0.shape
   if ( U0.ndim == 2 ): nx, ny = U0.shape

   UT = np.zeros((nt, nz, nx, ny))
   for it in range(nt):
     for iz in range(nz):
       if ( U0.ndim == 4 ):  UZ = U0[it, iz, :, :]
       if ( U0.ndim == 3 ):  UZ = U0[iz, :, :]
       if ( U0.ndim == 2 ):  UZ = U0[:, :]
       UT[it, iz, :, :] = scipy.interpolate.griddata((lonu.flatten(), latu.flatten()), UZ.flatten(), (lon,lat), method='linear', fill_value=0)
   UT = np.squeeze(UT)
   return UT

def regrid_UV(lonlat, Utuple, Vtuple ):
    (lon,lat)=lonlat
    (lonu, latu, U0) = Utuple
    (lonv, latv, V0) = Vtuple
    UT = np.zeros(U0.shape)
    UT = regrid_to_T((lon,lat), (lonu, latu, U0))
    VT = regrid_to_T((lon,lat), (lonv, latv, V0))
    return UT, VT

file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020110400.nc'
#dir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
ens_pre='GIOPS_E'
date=datetime.datetime(2020, 11, 4)

def check_ensembles(ensembles):
  if ( isinstance(ensembles, list) ):
    if ( len(ensembles) == 0 ): ensembles=range(nensembles)
  if ( isinstance(ensembles, str) ):
    if ( ensembles == 'd' or ensembles == 'D' ):
        pass
    else:
       try:
          ensembles = ENSEMBLES[int(ensembles)]
       except:
          try:
             ensembles = np.arange(int(ensembles))
          except:
             ensembles = []
  if ( isinstance(ensembles, int) ):
    ensembles=np.arange(ensembles)
  
  return ensembles
       
def read_ensemble(datadir, ens_pre, date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_', ensembles=[], date_anal=None):

    ensembles = check_ensembles(ensembles)
    ensstr=str(0)
    cyrs=[]
    print('ENSEMBLES = ', ensembles) 
    if ( ensembles == 'd' or ensembles == 'D' ):
      ensembles=[0]
      ensstr=''
    if ( ensembles == 'c' or ensembles == 'C' ):
      ensembles=list(range(5))
      cyrs=list(range(2015, 2023, 1))
      ensstr=''
    if ( len(ensembles) == 0 ): ensembles=range(nensembles)
    datestr=date.strftime("%Y%m%d%H")
    if  ( isinstance(date_anal, type(None)) ):
        datestd=datestr[:8]
    else:
        datestd=date_anal.strftime("%Y%m%d")

    if ( fld == 'T' ): var='thetao'
    if ( fld == 'Tsppt'): var='sppt_tem'
    if ( fld == 'S' ): var='so'
    if ( fld == 'Ssppt'): var='sppt_sal'
    if ( fld == 'U' ): var='uo'
    if ( fld == 'V' ): var='vo'
    if ( fld == 'H' ): var='zos'
    if ( fld == 'SST'): var='tos'
    if ( fld == 'SSU'): var='uos'
    if ( fld == 'SSV'): var='vos'
    if ( fld == 'U15'): var='uos'
    if ( fld == 'V15'): var='vos'
    if ( fld == 'MLD'): var='mldr10_1'
    if ( fld == 'TAUX'): var='TAUX'
    if ( fld == 'TAUY'): var='TAUY'
	
    grid='grid_'+fld
    if ( fld == 'S' ): grid='grid_'+'T'
    if ( fld == 'Tsppt'): grid='grid_'+'T'
    if ( fld == 'Ssppt'): grid='grid_'+'T'
    if ( fld == 'H' ): grid='grid_T_2D'
    if ( fld == 'SST'): grid='grid_T_2D'
    if ( fld == 'SSU'): grid='grid_U_2D'
    if ( fld == 'SSV'): grid='grid_V_2D'
    if ( fld == 'U15'): grid='grid_U_2D'
    if ( fld == 'V15'): grid='grid_V_2D'
    if ( fld == 'MLD'): grid='grid_T_2D'
    if ( fld == 'TAUX'): grid='gridU-RUN-crs'
    if ( fld == 'TAUY'): grid='gridV-RUN-crs'
    
    FLD_ENSEMBLE = []
    for ens in ensembles:
        if ( ensstr != '' ): ensstr=str(ens)
        if ( len(cyrs) > 0 ):
          datestr=date.strftime("%m%d%H")
          yearstr=string(cyrs[ens])
          datestr=yearstr+datestr
          if  ( isinstance(date_anal, type(None)) ):
              datestd=datestr[:8]
          else:
              datestd=yearstr+date_anal.strftime("%m%d")

        print( ens_pre, ensstr, datestd)        
        if  ( isinstance(date_anal, type(None)) ):
            file=datadir+'/'+ens_pre+ensstr+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc'
        else:
            file=datadir+'/'+ens_pre+ensstr+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr[:8]+'-'+datestr[:8]+'.nc'
        if ( fld == 'TAUX' or fld == 'TAUY' ):
            file=glob.glob(datadir+'/'+ens_pre+ensstr+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+'*'+'.nc')[0]
        print(file)
        if ( fld == 'U15' ):
            lon, lat, FLD10 = read_sam2_grid(file, fld='u10')
            lon, lat, FLD20 = read_sam2_grid(file, fld='u20')
            FLD = ( 2*FLD20 - FLD10 )   # SHORTHAND for (D20*FLD20 - D10*FLD10 ) / ( D20-D10 )
        elif ( fld == 'V15' ):   
            lon, lat, FLD10 = read_sam2_grid(file, fld='v10')
            lon, lat, FLD20 = read_sam2_grid(file, fld='v20')
            FLD = ( 2*FLD20 - FLD10 )   # SHORTHAND for (D20*FLD20 - D10*FLD10 ) / ( D20-D10 )
        else:
            lon, lat, FLD = read_sam2_grid(file, fld=var)
            #print(FLD.shape)
        FLD_ENSEMBLE.append(FLD)
    return lon, lat, FLD_ENSEMBLE

def read_ensemble_plus_depth(datadir, ens_pre, date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_', ensembles=[], date_anal=None):
    lon, lat, FLD_ENSEMBLE = read_ensemble(datadir, ens_pre, date, fld=fld, file_pre=file_pre, ensembles=ensembles, date_anal=date_anal)
    datestr=date.strftime("%Y%m%d%H")
    datestd=datestr[:8]
    grid='grid_'+fld
    if ( fld == 'S' ): grid='grid_'+'T'
    depvar='deptht'
    if ( fld == 'U' ): depvar='depthu'
    if ( fld == 'V' ): depvar='depthv'
    
    fil0=datadir+'/'+ens_pre+'0'+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc' 
    fila=datadir+'/'+ens_pre+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc' 
    try:
        depthT =  read_sam2_levels(fil0, fld=depvar)
    except:
        depthT = read_sam2_levels(fila, fld=depvar)
    return depthT, lon, lat, FLD_ENSEMBLE
       
def read_ensemble_plus_depthandtime(datadir, ens_pre, date, fld='T', time_fld='time_instant', file_pre='ORCA025-CMC-ANAL_1d_', ensembles=[], date_anal=None):
    lon, lat, FLD_ENSEMBLE = read_ensemble(datadir, ens_pre, date, fld=fld, file_pre=file_pre, ensembles=ensembles, date_anal=date_anal)
    datestr=date.strftime("%Y%m%d%H")
    if ( isinstance(date_anal, type(None)) ):
        datestd=datestr[:8]
    else:
        datestd=date_anal.strftime("%Y%m%d")
    grid='grid_'+fld
    if ( fld == 'S' ): grid='grid_'+'T'
    depvar='deptht'
    if ( fld == 'U' ): depvar='depthu'
    if ( fld == 'V' ): depvar='depthv'
    
    if ( isinstance(date_anal, type(None)) ):
        fil0=datadir+'/'+ens_pre+'0'+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc' 
        fila=datadir+'/'+ens_pre+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc' 
    else:
        fil0=datadir+'/'+ens_pre+'0'+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr[:8]+'-'+datestr[:8]+'.nc' 
        fila=datadir+'/'+ens_pre+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr[:8]+'-'+datestr[:8]+'.nc' 
        
    try:
        depthT =  read_sam2_levels(fil0, fld=depvar)
        times = read_sam2_times(file=fil0, fld=time_fld, T_ref=datetime.datetime(1950,1,1, 0,0,0,0, pytz.UTC))
    except:
        depthT = read_sam2_levels(fila, fld=depvar)
        times = read_sam2_times(file=fila, fld=time_fld, T_ref=datetime.datetime(1950,1,1, 0,0,0,0, pytz.UTC))
    
    return times, depthT, lon, lat, FLD_ENSEMBLE
    
def ensemble_mean(FLD_ENSEMBLE):
    FLD_MEAN = sum(FLD_ENSEMBLE) / len(FLD_ENSEMBLE)
    return FLD_MEAN

def ensemble_anomaly(FLD_ENSEMBLE):
    FLD_MEAN = ensemble_mean(FLD_ENSEMBLE)
    FLD_ANOMALY=[member-FLD_MEAN for member in FLD_ENSEMBLE]
    return FLD_ANOMALY, FLD_MEAN
    
def ensemble_square(FLD_ENSEMBLE):
    FLD_SQUARE=[np.square(member) for member in FLD_ENSEMBLE]
    return FLD_SQUARE
    
def ensemble_var(FLD_ENSEMBLE):
    FLD_ANOMALY, FLD_MEAN = ensemble_anomaly(FLD_ENSEMBLE)
    FLD_SQUARE = ensemble_square(FLD_ANOMALY)
    FLD_VARIANCE = ensemble_mean(FLD_SQUARE)
    return FLD_VARIANCE, FLD_MEAN

def fld_grad(H):
   nt=1
   nz=1
   if ( H.ndim == 4 ): nt, nz, nx, ny = H.shape
   if ( H.ndim == 3 ): nz, nx, ny = H.shape
   if ( H.ndim == 2 ): nx, ny = H.shape
   H3 = np.reshape(H, (nt*nz,nx,ny))
   DHDX = np.zeros((nt*nz,nx,ny))
   DHDY = np.zeros((nt*nz,nx,ny))
   for iz in range(nt*nz):
     for ix in range(1, nx-1):
       DHDX[iz,ix,:] = ( H3[iz,ix+1,:] - H3[iz,ix,:]) / e1u[ix,:]
     DHDX[iz,  0, :] = DHDX[iz, -2, :]
     DHDX[iz, -1, :] = DHDX[iz,  1, :]
     for iy in range(ny-1):
       DHDY[iz,:,iy] = (H3[iz,:,iy+1] - H3[iz,:,iy]) / e2v[:,iy]
     # NEED north fold condition???
     for ix in range(nx):
       DHDY[iz,nx-ix-1,ny-1] = DHDY[iz, ix, ny-3]
   DHDX = np.squeeze(np.reshape(DHDX, (nt,nz,nx,ny)))
   DHDY = np.squeeze(np.reshape(DHDY, (nt,nz,nx,ny)))
   return DHDX, DHDY

def geostrophic_V(dhdx, dhdy):
    g=9.7976
    omega=7.292e-5
    C = 0.5 * g / omega
    u_atV = -1.0 * C * dhdy
    v_atU =  1.0 * C * dhdx
    
    uT = regrid_VtoT(u_atV)
    vT = regrid_UtoT(v_atU)
    return uT, vT
           
def plot_date(date, ens_pre='GIOPS_E', pdir='EFIG',ensembles=[], ddir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'):
    datestr=date.strftime("%Y%m%d")
    file_pre='ORCA025-CMC-ANAL_1d_'           
    for fld in ['T', 'S', 'U', 'H']:
        file_pre='ORCA025-CMC-ANAL_1d_'      
        if ( fld == 'H' ):  file_pre='ORCA025-CMC-ANAL_1h_'     
        lon, lat, FLD_ENSEMBLE = read_ensemble(ddir, ens_pre, date, fld=fld, file_pre=file_pre, ensembles=ensembles)
        if ( fld == 'U' ):  lonv, latv, FLV_ENSEMBLE = read_ensemble(ddir, ens_pre, date, fld='V', file_pre=file_pre, ensembles=ensembles)
        #if ( fld == 'H' ): 
        #   lont = lon
        #   latt = lat
        if ( fld == 'T' ): 
            lont = lon
            latt = lat
        if ( fld == 'U' ): 
            lonu = lon
            latu = lat

        if ( (fld == 'T') or (fld == 'S') ):  
            # Easier to use depth_mean function (does not actually have anything to do with velocity)
            FLD_EXTRA = [ isoheatcontent.depth_mean_velocity(np.squeeze(T_3D), e3t, mask, depth=100) for T_3D in FLD_ENSEMBLE ]
            FLD_XXTRA = [ isoheatcontent.depth_mean_velocity(np.squeeze(T_3D), e3t, mask, depth=1000) for T_3D in FLD_ENSEMBLE ]
            FLD_ENSEMBLE = [ np.squeeze(T_3D[0,0,:,:]) for T_3D in FLD_ENSEMBLE ]
        if ( fld == 'H' ):
            FLD_ENSEMBLE = [ np.mean(H_3D, axis=(0)) for H_3D in FLD_ENSEMBLE ]
            FLD_EXTRA = []
            FLD_XXTRA = []
            VGEO_ENSEMBLE = []
            ne = len(FLD_ENSEMBLE)
            for ie in range(ne):
                HFLD = FLD_ENSEMBLE[ie]
                DHDX, DHDY = fld_grad(HFLD)
                UGEO, VGEO = geostrophic_V(DHDX, DHDY)
                KE = 0.5 * ( np.square(UGEO) + np.square(VGEO) )
                FLD_EXTRA.append(KE)
                FLD_XXTRA.append(HFLD)
        if ( fld == 'U' ):  
            # Easier to use depth_mean function (does not actually have anything to do with velocity)
            FLD_EXTRA = []
            FLV_EXTRA = []
            FLD_XXTRA = []
            FLV_XXTRA = []
            for ie, U_3D in enumerate(FLD_ENSEMBLE):
                V_3D = FLV_ENSEMBLE[ie]
                u_20, zthicku_20 = isoheatcontent.depth_integral(np.squeeze(U_3D), e3u, masku, depth=20)
                u_10, zthicku_10 = isoheatcontent.depth_integral(np.squeeze(U_3D), e3u, masku, depth=10)
                u_4c, zthicku_4c = isoheatcontent.depth_integral(np.squeeze(U_3D), e3u, masku, depth=400)
                u_6c, zthicku_6c = isoheatcontent.depth_integral(np.squeeze(U_3D), e3u, masku, depth=600)
                #Note:  u_10 and u_20 are depth INTEGRALS.
                u_15 = ( u_20 - u_10 ) / 10
                u_5c = ( u_6c - u_4c ) / 200
                v_20, zthickv_20 = isoheatcontent.depth_integral(np.squeeze(V_3D), e3v, maskv, depth=20)
                v_10, zthickv_10 = isoheatcontent.depth_integral(np.squeeze(V_3D), e3v, maskv, depth=10)
                v_4c, zthickv_4c = isoheatcontent.depth_integral(np.squeeze(V_3D), e3v, maskv, depth=400)
                v_6c, zthickv_6c = isoheatcontent.depth_integral(np.squeeze(V_3D), e3v, maskv, depth=600)
                #Note:  v_10 and v_20 are depth INTEGRALS.
                v_15 = ( v_20 - v_10 ) / 10
                v_5c = ( v_6c - v_4c ) / 200
                FLD_EXTRA.append(u_15)
                FLV_EXTRA.append(v_15)
                FLD_XXTRA.append(u_5c)
                FLV_XXTRA.append(v_5c)
            FLD_ENSEMBLE = [ np.squeeze(U_3D[0,0,:,:]) for U_3D in FLD_ENSEMBLE]
            FLV_ENSEMBLE = [ np.squeeze(V_3D[0,0,:,:]) for V_3D in FLV_ENSEMBLE]
            NEW_ENSEMBLE = []
            NEW_EXTRA = []
            NEW_XXTRA = []
            for ie, Uo in enumerate(FLD_ENSEMBLE):
                Vo = FLV_ENSEMBLE[ie]
                U15 = FLD_EXTRA[ie]
                V15 = FLV_EXTRA[ie]
                U5c = FLD_XXTRA[ie]
                V5c = FLV_XXTRA[ie]
                UT = regrid_UtoT(Uo)
                VT = regrid_VtoT(Vo)
                #UT, VT = regrid_UV((lont,latt), (lonu, latu, U0), (lonv, latv, V0))
                NEW_ENSEMBLE.append( np.square(UT)+np.square(VT) )
                UT = regrid_UtoT(U15)
                VT = regrid_VtoT(V15)
                NEW_EXTRA.append( np.square(UT)+np.square(VT) )
                UT = regrid_UtoT(U5c)
                VT = regrid_VtoT(V5c)
                NEW_XXTRA.append( 0.5*(np.square(UT)+np.square(VT) ) )
            FLD_ENSEMBLE = NEW_ENSEMBLE
            FLD_EXTRA = NEW_EXTRA           
            FLD_XXTRA = NEW_XXTRA           
        FLD_var, FLD_mean = ensemble_var(FLD_ENSEMBLE)
        EXT_var, EXT_mean = ensemble_var(FLD_EXTRA)
        XXT_var, EXT_mean = ensemble_var(FLD_XXTRA)
        FLD_std = np.sqrt(FLD_var)
        EXT_std = np.sqrt(EXT_var)
        XXT_std = np.sqrt(XXT_var)
    
        GLO_std = area_wgt_average.area_wgt_average(FLD_std)
        GLX_std = area_wgt_average.area_wgt_average(EXT_std)
        GLY_std = area_wgt_average.area_wgt_average(XXT_std)
        dateint = int(datestr)
        #pdir='/home/dpe000/EnGIOPS/EFIG'
        outfile=TOPDIR+'/'+pdir+'/'+fld+'_glostd.dat'
        print(fld, [GLO_std, GLX_std, GLY_std])
        datadatefile.add_to_file(dateint, [GLO_std, GLX_std, GLY_std], file=outfile)

        cmap_anom = 'seismic'
        cmap_posd = 'gist_stern_r'
        if ( fld == 'T' ):
            title = 'SST ensemble standard deviation on '+datestr
            xitle = '0-100m T ensemble standard deviation on '+datestr
            yitle = '0-1000m T ensemble standard deviation on '+datestr
            CLEV=np.arange(0, 1.1,0.1)
        if ( fld == 'S' ):
            title = 'SSS ensemble standard deviation on '+datestr
            xitle = '0-100m S ensemble standard deviation on'+datestr
            yitle = '0-1000m S ensemble standard deviation on'+datestr
            CLEV=np.arange(0, 0.55,0.05)
        if ( fld == 'U' ):
            title = 'Surface KE standard deviation on '+datestr
            xitle = '15m KE standard deviation on '+datestr
            yitle = '500m KE standard deviation on '+datestr
            CLEV=np.arange(0, 0.275,0.025)
        if ( fld == 'H' ):
            title = '$\eta$ ensemble standard deviation on '+datestr
            xitle = 'Geostophic KE standard deviation on '+datestr
            yitle = '$\eta$ ensemble standard deviation on '+datestr
            CLEV=np.arange(0, 0.22,0.02)
        outfile=TOPDIR+'/'+pdir+'/'+fld+'_std_'+datestr+'.png'
        ouxfile=TOPDIR+'/'+pdir+'/'+fld+'X_std_'+datestr+'.png'
        ouyfile=TOPDIR+'/'+pdir+'/'+fld+'Y_std_'+datestr+'.png'
        print('SHAPE', FLD_std.shape, EXT_std.shape, XXT_std.shape)
        print('Max', np.max(FLD_std), np.max(EXT_std))
        cplot.grd_pcolormesh(lon, lat, FLD_std, levels=CLEV, cmap=cmap_posd, outfile=outfile, project='PlateCarree', title=title, obar='horizontal')
        cplot.grd_pcolormesh(lon, lat, EXT_std, levels=CLEV, cmap=cmap_posd, outfile=ouxfile, project='PlateCarree', title=xitle, obar='horizontal')
        cplot.grd_pcolormesh(lon, lat, XXT_std, levels=CLEV, cmap=cmap_posd, outfile=ouyfile, project='PlateCarree', title=yitle, obar='horizontal')
    return
    
def extract_slice(FLD_LIST, slice=0, axis=0):
    NEW_LIST=[]
    for FLD in FLD_LIST:
        if ( axis == 0 ):
            NEW=(FLD[[slice],:])
        if ( axis == 1 ):
            NEW=(FLD[:,[slice],:])
        NEW_LIST.append(NEW)
    return NEW_LIST
            
def plot_ratios(date, ens_pre='GIOPS_E', pdir='EFIG',ensembles=[], ddir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'):
    datestr=date.strftime("%Y%m%d")
    file_analy='ORCA025-CMC-ANAL_1d_'   
    file_trial='ORCA025-CMC-TRIAL_1d_'     

    kappa_list = [] 
    for fld in ['T', 'S', 'H']:
        file_analy='ORCA025-CMC-ANAL_1d_'      
        file_trial='ORCA025-CMC-TRIAL_1d_'     
        inflate = 24.0/12.0   ##  Inflate ratios by two as average is over full IAU period.  
        if ( fld == 'H' ):  
            file_analy='ORCA025-CMC-ANAL_1h_'     
            file_trial='ORCA025-CMC-TRIAL_1h_'  
            inflate=24.0/23.5   

        lon, lat, FLD_ANALY = read_ensemble(ddir, ens_pre, date, fld=fld, file_pre=file_analy, ensembles=ensembles)
        lon, lat, FLD_TRIAL = read_ensemble(ddir, ens_pre, date, fld=fld, file_pre=file_trial, ensembles=ensembles)
        # ONLY NEED LAST DAY/HOUR
        FLD_ANALY=extract_slice(FLD_ANALY, slice=-1)
        FLD_TRIAL=extract_slice(FLD_TRIAL, slice=-1)
        
        if ( fld == 'T' ): 
            lont = lon
            latt = lat

        print(FLD_ANALY[0].shape, FLD_TRIAL[0].shape, len(FLD_ANALY), len(FLD_TRIAL) )
        ANALY_var, ANALY_mean = ensemble_var(FLD_ANALY)
        TRIAL_var, TRIAL_mean = ensemble_var(FLD_TRIAL)

        print(ANALY_var.shape, TRIAL_var.shape, ANALY_mean.shape, TRIAL_mean.shape)
        
        gamma = ( ANALY_var / TRIAL_var )
        print('Ratio Max = ', np.max(gamma))
        EXCEED = np.where(gamma > 1)
        gamma[EXCEED] = 1.0
        print('Capped Max = ', np.max(gamma))
        
        kappa = np.squeeze(1 - gamma)
        kappa_list.append(kappa)

        cmap_posd = 'gist_stern_r'
        CLEV = np.arange(0, 0.65, 0.05)
        title=datestr+" "+fld+" GAIN"
        outfile=TOPDIR+'/'+pdir+'/'+fld+'_gain_'+datestr+'.png'
        KAPPA=np.squeeze(kappa)
        if ( KAPPA.ndim > 2):  KAPPA=KAPPA[0,:,:]
        print(fld+' Max: ', np.max(KAPPA))
        cplot.grd_pcolormesh(lon, lat, KAPPA, levels=CLEV, cmap=cmap_posd, outfile=outfile, project='PlateCarree', title=title, obar='horizontal')

    global_mean = global_average_field(kappa_list, areaF=e1t*e2t, maskF=mask)
    global_mean_longlist = make_super_list(global_mean)
    outfile=TOPDIR+'/'+pdir+'/'+'GLOgain.dat'
    dateint=int(datestr)
    datadatefile.add_to_file(dateint, global_mean_longlist, file=outfile)
    
    outfile=TOPDIR+'/'+pdir+'/'+'Kgain_'+datestr+'.nc'
    rc = write_nc_grid.write_nc3d_grid(kappa_list, ['T','S','H'], [3,3,2], outfile)

    return kappa_list

def global_average_field(fld, areaF=e1t*e2t, maskF=mask):
    if ( isinstance(fld, list) ):
        global_mean_list = []
        for FLD in fld:
            global_mean = global_average_field(FLD, areaF=areaF, maskF=maskF)
            global_mean_list.append(global_mean) 
        return global_mean_list
    if ( ( isinstance(fld, np.ndarray) ) or ( isinstance(fld, numpy.ma.core.MaskedArray) )):
        (nt, nz) = (1,1)
        if ( fld.ndim == 4 ): nt, nz, nx, ny = fld.shape
        if ( fld.ndim == 3 ): nz,nx,ny=fld.shape
        global_mean_list = []
        for it in range(nt):
          for iz in range(nz):
            if ( fld.ndim == 4 ): FLD=fld[it, iz, : , :]
            if ( fld.ndim == 3 ): FLD=fld[iz,:,:]
            if ( fld.ndim == 2): FLD=fld[:,:]
            global_mean = area_wgt_average.area_wgt_average(FLD, area=areaF*maskF[iz,:,:])
            global_mean_list.append(global_mean)
        if ( ( nt > 1 ) or ( nz > 1 ) ) :
          global_mean_array = np.squeeze(np.reshape(np.array(global_mean_list), (nt,nz)))
        else:
          global_mean_array = global_mean_list[0]
        return global_mean_array
    return
    
def make_super_list(list):
    super_list = []
    for elem in list:
        if ( isinstance(elem, np.ndarray) ):
            super_list.extend( np.ndarray.tolist(elem) )
        else:
            super_list.append(elem)
    return super_list            

def read_kappa_ncfile(file, flds=['T','S','H']):
    LIST = write_nc_grid.read_nc(file,flds)
    return LIST
        
def loop_calc_ratio( date_range, pdir='EFIG'):   
    date_start = date_range[0]
    date_final = date_range[1]
    FLDS=['T','S','H']
    if ( ( isinstance(date_start, str) ) or ( isinstance(date_start, int) ) ): date_start = datadatefile.convert_strint_date(date_start)
    if ( ( isinstance(date_final, str) ) or ( isinstance(date_final, int) ) ): date_final = datadatefile.convert_strint_date(date_final)
    date_incre=7
    if ( len(date_range) > 2 ): date_incre=date_range[2]
    date_loop = date_start
    ninc=0
    kappa_sum_list = []
    while ( date_loop <= date_final ):
        datestr=date_loop.strftime("%Y%m%d")
        ncfile=TOPDIR+'/'+pdir+'/'+'Kgain_'+datestr+'.nc'
        kappa_list = read_kappa_ncfile(ncfile, flds=FLDS)
        for ilist, kappa in enumerate(kappa_list):
            KAPPA = np.squeeze(kappa)
            if ( ninc == 0 ): 
                kappa_sum_list.append(KAPPA)
            else:
                kappa_sum = kappa_sum_list[ilist]
                kappa_sum = kappa_sum+KAPPA
                kappa_sum_list[ilist] = kappa_sum
        date_loop = date_loop + datetime.timedelta(days=date_incre)
        ninc=ninc+1

    cmap_posd = 'gist_stern_r'
    CLEV = np.arange(0, 0.65, 0.05)
    kappa_mean_list = []
    for ilist, kappa_sum in enumerate(kappa_sum_list):
        fld=FLDS[ilist]
        kappa_sum = kappa_sum / ninc
        kappa_mean_list.append(kappa_sum)
        KAPPA=np.squeeze(kappa_sum)
        nz=1
        if ( KAPPA.ndim > 2 ): nz=len(KAPPA)
        for iz in range(nz):
            if ( nz == 1 ): 
                KPLOT=KAPPA
                zfld=fld
            else:
                KPLOT=KAPPA[iz,:,:]
                zfld=fld+'.'+str(iz).zfill(2)
            title='Time Average'+" "+zfld+" GAIN"
            outfile=TOPDIR+'/'+pdir+'/'+zfld+'_gain_'+'TAVERAGE'+'.png'
            cplot.grd_pcolormesh(nav_lon, nav_lat, KPLOT, levels=CLEV, cmap=cmap_posd, outfile=outfile, project='PlateCarree', title=title, obar='horizontal')

    global_mean = global_average_field(kappa_mean_list, areaF=nav_area, maskF=mask)
    print('Global Mean T: ', global_mean[0])
    print('Global Mean S: ', global_mean[1])
    print('Global Mean H: ', global_mean[2])
    return

def_plots=[ [['T',0,'SST'], ['T',1,'T(0-100m)'] ,['T',2, 'T(0-1000m)']], 
            [['S',0,'SSS'], ['S',1,'S(0-100m)'],['S',2,'S(0-1000m)']], 
            [['H',0,'$\eta$']], 
            [['U',0,'KE(0m)'], ['U',1,'KE(15m)'], ['U',2,'KE(500m)'], ['H',1,'KE(geo)']] 
          ]
def_ylabels=[['Temperature', '($\deg$C)','T'], ['Salinity', '(PSU)','S'], ['Sea Surface Height', '(m)','H'], ['Kinetic Energy', '(m$^2$/s$^2$)','U']]
def_time=[datetime.datetime(2019,3,13), datetime.datetime(2020,12,30)]


def plot_timeseries(pdir='EFIG', plots=def_plots, ylabels=def_ylabels, time_range=None):

    plt.rc('font', family='serif')
    #plt.rc('text', usetex=True)

    #types = [ plot[0] for plot in plots ]    
    myFmt = mdates.DateFormatter('%m/%d')
    dates_list = []
    serie_list = []
    colours = ['r', 'b', 'g', 'm', 'c']
    for iplot, myplot in enumerate(plots):
        ylabel = 'Std Dev of '+ylabels[iplot][0]+' '+ylabels[iplot][1]
        ititle = 'Std Dev '+ylabels[iplot][0]+' time series'
        iofile = ylabels[iplot][2]
        fig, ax = plt.subplots()
        dates_list = []
        serie_list = []
        for itype, mytype in enumerate(myplot):
            icolor = colours[itype]
            hitype = mytype[0]
            iitype = mytype[1]
            ilabel = mytype[2]
            
            dfile=TOPDIR+'/'+pdir+'/'+hitype+'_glostd.dat'
            print(dfile)
            dateint_list, STD = datadatefile.read_file(dfile)
            dates = datadatefile.convert_strint_datelist(dateint_list)
            iSTD = STD[iitype]
            dates_list.append(dates)
            serie_list.append(iSTD)
            ax.plot(dates, iSTD, color=icolor, linestyle='-', label=ilabel)

        ax.legend()
        ax.set_ylabel(ylabel)
        ax.set_xlabel('Date')
        ax.set_title(ititle)

        outfile=TOPDIR+'/'+pdir+'/'+iofile+'_timeseries'
        fig.savefig(outfile+'.png')
        fig.savefig(outfile+'.pdf')
        plt.close(fig)
    return
                
def plot_multi_timeseries(outprefix='PLOTS/', pdirs=['EFIG','TFIG'], labels=['Flx', 'Flx+STO'], plots=def_plots, ylabels=def_ylabels, time_range=None):

    plt.rc('font', family='serif')
    #plt.rc('text', usetex=True)

    myFmt = mdates.DateFormatter('%m/%d')
    colours = ['r', 'b', 'g', 'm', 'c']
    linesty = ['-', '--', ':', '-.']

    figs = []
    axes = []
    for iplot, myplot in enumerate(plots):
        ylabel = 'Std Dev of '+ylabels[iplot][0]+' '+ylabels[iplot][1]
        ititle = 'Std Dev '+ylabels[iplot][0]+' time series'
        iofile = ylabels[iplot][2]
        fig, axe = plt.subplots()
        figs.append(fig)
        axes.append(axe)
    
        dates_list = []
        serie_list = []
        legend_expts = []
        legend_elements = []
        for itype, mytype in enumerate(myplot):
            linestyle = linesty[itype]
            hitype = mytype[0]
            iitype = mytype[1]
            ilabel = mytype[2]
            legend_elements.append( Line2D([0], [0], color='k', ls=linestyle, label=ilabel) )
            
            for idir, pdir in enumerate(pdirs):
                icolor = colours[idir%5]
                label = labels[idir]
                dfile=TOPDIR+'/'+pdir+'/'+hitype+'_glostd.dat'
                print(dfile)
                dateint_list, STD = datadatefile.read_file(dfile)
                dates = datadatefile.convert_strint_datelist(dateint_list)
                iSTD = STD[iitype]
                dates_list.append(dates)
                serie_list.append(iSTD)
                eline, = axe.plot(dates, iSTD, color=icolor, linestyle=linestyle, label=label)
                if ( itype == 0 ):
                    legend_expts.append(eline)
                
        #print(legend_expts)
        #print(legend_elements)
        expt_legend = axe.legend(handles=legend_expts, loc='lower right')
        line_legend = axe.legend(handles=legend_elements, loc='upper left')
        axe.add_artist(expt_legend)
        axe.add_artist(line_legend)
        axe.set_ylabel(ylabel)
        axe.set_xlabel('Date')
        axe.set_title(ititle)

        outfile=TOPDIR+'/'+outprefix+iofile+'_timeseries'
        fig.savefig(outfile+'.png')
        fig.savefig(outfile+'.pdf')
        plt.close(fig)
        
    return

def_ylabels=[['Temperature', '($\deg$C)','T'], ['Salinity', '(PSU)','S'], ['Sea Surface Height', '(m)','H'], ['Kinetic Energy', '(m$^2$/s$^2$)','U']]
def_time=[datetime.datetime(2019,3,13), datetime.datetime(2020,12,30)]

def plot_multi_ratioseries(outprefix='PLOTS/E20_', pdirs=['EFIG','TFIG', 'SFIG'], labels=['Flx', 'Flx+STO', 'STO'], time_range=None):

    plt.rc('font', family='serif')
    #plt.rc('text', usetex=True)

    myFmt = mdates.DateFormatter('%m/%d')
    colours = ['r', 'b', 'g', 'm', 'c']
    linesty = ['-', '--', ':', '-.']

    figs = []
    axes = []

    ZED = read_sam2_levels()
    
    IDEP = [0]
    ZDEP = [0, 10, 100, 1000]
    for zdep in ZDEP[1:]:
        idep = np.argmin(np.abs(ZED-zdep))
        IDEP.append(idep)
        
    dates_list = []
    gains_list = []
    for idir, pdir in enumerate(pdirs):
        dfile=TOPDIR+'/'+pdir+'/GLOgain.dat'
        dateint_list, gains = datadatefile.read_file(dfile)
        dates = datadatefile.convert_strint_datelist(dateint_list)
        dates_list.append(dates)
        gains_list.append(gains)
        
    for iplot in range(104):
        if ( iplot < 50 ):
            TFLD='T'
            OFLD='T'
            LEV=str(iplot)
            IIS=[iplot]
            ilabels=['T['+LEV+']']
        elif ( iplot < 100 ):
            TFLD='S'
            OFLD='S'
            LEV=str(iplot-50)
            IIS=[iplot]
            ilabels=['S['+LEV+']']
        elif ( iplot == 100):
            TFLD='$\eta$'
            OFLD='H'
            LEV='0'
            IIS=[iplot]
            ilabels=['$\eta$']
        elif ( iplot == 101):
            TFLD='T/S/H'
            OFLD='A'
            LEV='0'
            IIS=[0, 50, 100]
            ilabels=['T[0]', 'S[0]', '$\eta$']
        elif ( iplot == 102):
            TFLD='T'
            OFLD='T'
            LEV='M'
            IIS=IDEP
            ilabels=['T[0m]', 'T[10m]', 'T[100m]', 'T[1000m]']
        elif ( iplot == 102):
            TFLD='S'
            OFLD='S'
            LEV='M'
            IIS=[50+idep for idep in IDEP]
            ilabels=['S[0m]', 'S[10m]', 'S[100m]', 'S[1000m]']
            
        ylabel = 'Gain $\kappa$ for '+TFLD+'L'+LEV
        ititle = 'Gain $\kappa$ for '+TFLD+'L'+LEV+' time series'
        iofile = OFLD+'L'+LEV
        fig, axe = plt.subplots()
        figs.append(fig)
        axes.append(axe)
    
        legend_expts = []
        legend_elements = []
        
        for idir, pdir in enumerate(pdirs):
            icolor = colours[idir%5]
            label = labels[idir]
            dates = dates_list[idir]
            gains = gains_list[idir]
            dfile=TOPDIR+'/'+pdir+'/GLOgain.dat'
            
            Tgain = gains[0:50,:]
            Sgain = gains[50:100,:]
            Hgain = gains[100,:]

            idata = gains[IIS,:]
            if ( idata.ndim == 1 ):
               idata = [idata.tolist()]
            else:
               idata = idata.tolist()
        
            for itype in range(len(idata)):
                linestyle = linesty[itype]
                ilabel = ilabels[itype]                
                if ( idir == 0 ): legend_elements.append( Line2D([0], [0], color='k', ls=linestyle, label=ilabel) )
                eline, = axe.plot(dates, idata[itype], color=icolor, linestyle=linestyle, label=label)
                if ( itype == 0 ):
                    legend_expts.append(eline)
            
        #print(legend_expts)
        #print(legend_elements)
        expt_legend = axe.legend(handles=legend_expts, loc='lower right')
        line_legend = axe.legend(handles=legend_elements, loc='upper left')
        axe.add_artist(expt_legend)
        axe.add_artist(line_legend)
        axe.set_ylabel(ylabel)
        axe.set_xlabel('Date')
        axe.set_title(ititle)

        outfile=TOPDIR+'/'+outprefix+iofile+'_timeseries'
        fig.savefig(outfile+'.png')
        fig.savefig(outfile+'.pdf')
        plt.close(fig)
        
    return
