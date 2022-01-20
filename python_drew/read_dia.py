
import sys
this_dir='/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python_drew'
sys.path.insert(0, this_dir)
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import os.path
import netCDF4
import scipy.interpolate

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import read_grid
import isoheatcontent
import cplot
#import find_hall
import area_wgt_average
import datadatefile

#hall = find_hall.find_hall()
nensembles=21
file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020110400.nc'
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
    
    return lon, lat, TM
    
def read_sam2_grid_t(file):
    lon, lat, TM = read_sam2_grid(file,'thetao')
    __, __, SALW = read_sam2_grid(file, 'so')
    return lon, lat, TM, SALW

filu='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_U_2020110400.nc'
filv='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_V_2020110400.nc'
filh='fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1h_grid_T_2D_2020110400.nc'

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
    
    
def regrid_to_T((lon, lat), (lonu, latu, U0)):
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

def regrid_UV((lon,lat), (lonu, latu, U0), (lonv, latv,V0) ):
    UT = np.zeros(U0.shape)
    UT = regrid_to_T((lon,lat), (lonu, latu, U0))
    VT = regrid_to_T((lon,lat), (lonv, latv, V0))
    return UT, VT

file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2/20201104/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020110400.nc'
dir='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives'
ens_pre='GIOPS_E'
date=datetime.datetime(2020, 11, 04)

def read_ensemble(dir, ens_pre, date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_', ensembles=[]):

    if ( len(ensembles) == 0 ): ensembles=range(nensembles)
    datestr=date.strftime("%Y%m%d%H")
    datestd=datestr[:8]

    if ( fld == 'T' ): var='thetao'
    if ( fld == 'S' ): var='so'
    if ( fld == 'U' ): var='uo'
    if ( fld == 'V' ): var='vo'
    if ( fld == 'H' ): var='zos'

    grid='grid_'+fld
    if ( fld == 'S' ): grid='grid_'+'T'
    if ( fld == 'H' ): grid='grid_T_2D'
    FLD_ENSEMBLE = []
    for ens in ensembles:
        ensstr=str(ens)
	file=dir+'/'+ens_pre+ensstr+'/SAM2/'+datestd+'/'+'DIA/'+file_pre+grid+'_'+datestr+'.nc'
	print(file)
	lon, lat, FLD = read_sam2_grid(file, fld=var)
	FLD_ENSEMBLE.append(FLD)
    return lon, lat, FLD_ENSEMBLE
 
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
           
def plot_date(date):
    datestr=date.strftime("%Y%m%d")
    file_pre='ORCA025-CMC-ANAL_1d_'           
    for fld in ['T', 'S', 'U', 'H']:
        file_pre='ORCA025-CMC-ANAL_1d_'      
	if ( fld == 'H' ):  file_pre='ORCA025-CMC-ANAL_1h_'     

        lon, lat, FLD_ENSEMBLE = read_ensemble(dir, ens_pre, date, fld=fld, file_pre=file_pre)
	if ( fld == 'U' ):  lonv, latv, FLV_ENSEMBLE = read_ensemble(dir, ens_pre, date, fld='V', file_pre=file_pre)
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
        pdir='/home/dpe000/EnGIOPS/EFIG'
        outfile=pdir+'/'+fld+'_glostd.dat'
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
        outfile=pdir+'/'+fld+'_std_'+datestr+'.png'
        ouxfile=pdir+'/'+fld+'X_std_'+datestr+'.png'
        ouyfile=pdir+'/'+fld+'Y_std_'+datestr+'.png'
	print('SHAPE', FLD_std.shape, EXT_std.shape, XXT_std.shape)
	print('Max', np.max(FLD_std), np.max(EXT_std))
        cplot.grd_pcolormesh(lon, lat, FLD_std, levels=CLEV, cmap=cmap_posd, outfile=outfile, project='PlateCarree', title=title, obar='horizontal')
        cplot.grd_pcolormesh(lon, lat, EXT_std, levels=CLEV, cmap=cmap_posd, outfile=ouxfile, project='PlateCarree', title=xitle, obar='horizontal')
        cplot.grd_pcolormesh(lon, lat, XXT_std, levels=CLEV, cmap=cmap_posd, outfile=ouyfile, project='PlateCarree', title=yitle, obar='horizontal')
    return

def_plots=[ [['T',0,'SST'], ['T',1,'T(0-100m)'] ,['T',2, 'T(0-1000m)']], 
            [['S',0,'SSS'], ['S',1,'S(0-100m)'],['S',2,'S(0-1000m)']], 
	    [['H',0,'$\eta$']], 
	    [['U',0,'KE(0m)'], ['U',1,'KE(15m)'], ['U',2,'KE(500m)'], ['H',1,'KE(geo)']] 
	  ]
def_ylabels=[['Temperature', '($\deg$C)','T'], ['Salinity', '(PSU)','S'], ['Sea Surface Height', '(m)','H'], ['Kinetic Energy', '(m$^2$/s$^2$)','U']]
def_time=[datetime.datetime(2019,3,13), datetime.datetime(2020,12,30)]
def plot_timeseries(pdir='/home/dpe000/EnGIOPS/EFIG', plots=def_plots, ylabels=def_ylabels, time_range=None):

    plt.rc('font', family='serif')
    plt.rc('text', usetex=True)

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
	    
            dfile=pdir+'/'+hitype+'_glostd.dat'
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

        fig.savefig(pdir+'/'+iofile+'_timeseries.png')
        fig.savefig(pdir+'/'+iofile+'_timeseries.pdf')
        plt.close(fig)
        	
