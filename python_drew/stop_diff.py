import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import netCDF4

import read_dia
import read_grid
import datadatefile
import isoheatcontent
import cplot

stofile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_STOP/SAM2/20190313.10/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'
reffile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_DNH0/SAM2/20190313/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'

cmap_anom = 'seismic'
cmap_posd = 'gist_stern_r'

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

def plot_fld_diff(stofile, reffile=reffile, pdir='SDIF', psuf='', CLEV=np.arange(-0.9,1.1,0.2), comment=None):
    lon, lat, T_sto, S_sto = read_dia.read_sam2_grid_t(stofile)
    lon, lat, T_ref, S_ref = read_dia.read_sam2_grid_t(reffile)

    Tdf = np.squeeze(T_sto-T_ref)
    Sdf = np.squeeze(S_sto-S_ref)

    print('SHAPE', Tdf.shape, Sdf.shape)

    SST = Tdf[0,:,:]
    SSS = Sdf[0,:,:]
    TD1 = isoheatcontent.heat_content_diff(Tdf, e3t, mask, depth=[1, 10])
    SD1 = isoheatcontent.salt_content_diff(Sdf, e3t, mask, depth=[1, 10])
    TC1 = isoheatcontent.heat_content_diff(Tdf, e3t, mask, depth=[10, 100])
    SC1 = isoheatcontent.salt_content_diff(Sdf, e3t, mask, depth=[10, 100])
    TC5 = isoheatcontent.heat_content_diff(Tdf, e3t, mask, depth=[100, 500])
    SC5 = isoheatcontent.salt_content_diff(Sdf, e3t, mask, depth=[100, 500])

    TD1 = isoheatcontent.heat_to_degC(TD1, depth=9, anomaly=True )
    TC1 = isoheatcontent.heat_to_degC(TC1, depth=90, anomaly=True)
    TC5 = isoheatcontent.heat_to_degC(TC5, depth=400, anomaly=True)
    SD1 = isoheatcontent.salt_to_PSU(TD1, depth=9)
    SC1 = isoheatcontent.salt_to_PSU(TC1, depth=90)
    SC5 = isoheatcontent.salt_to_PSU(TC5, depth=400)

    print('Max/Min', np.max(SST), np.min(SST))
    print('Max/Min', np.max(SSS), np.min(SSS))

    title='SST Anomaly'
    cplot.grd_pcolormesh(lon, lat, SST, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'SST.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='SSS Anomaly'
    cplot.grd_pcolormesh(lon, lat, SSS, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'SSS.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='T(1-10m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, TD1, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'TD1.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='S(1-10m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, SD1, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'SD1.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='T(10-100m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, TC1, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'TC1.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='S(10-100m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, SC1, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'SC1.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='T(100-500m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, TC5, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'TC5.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')
    title='S(100-500m) Anomaly'
    cplot.grd_pcolormesh(lon, lat, SC5, levels=CLEV, cmap=cmap_anom, outfile=pdir+'/'+'SC5.'+psuf+'.png', project='PlateCarree', title=title, suptitle=comment, obar='horizontal')

    return
