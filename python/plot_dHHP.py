import xarray  as xr
import sys
import numpy as np
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import cplot
import rank_histogram

#D1O=xr.open_dataset('/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs/Oper_no_us_argo/SAM2/20201230/DIA/ORCA025-CMC-TRIAL_1d_grid_T_2D_2020123000.nc')
#D2O=xr.open_dataset('/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs/Oper/SAM2/20201230/DIA/ORCA025-CMC-TRIAL_1d_grid_T_2D_2020123000.nc')

dates=rank_histogram.create_dates(20200610, 20201104, 7)
str_dates=[date.strftime("%Y%m%d") for date in dates]

pre1='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs/Oper/SAM2/'
pre2='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs/Oper_no_us_argo/SAM2/'
pre3='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs/NoArgoV2/SAM2/'

file1=[pre1+date+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_2D_'+date+'00.nc' for date in str_dates]
file2=[pre2+date+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_2D_'+date+'00.nc' for date in str_dates]
file3=[pre3+date+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_2D_'+date+'00.nc' for date in str_dates]
D1=xr.open_mfdataset(file1)
D2=xr.open_mfdataset(file2)
D3=xr.open_mfdataset(file3)

HHP1=D1['hhp']; print(HHP1.shape)
HHP2=D2['hhp']; print(HHP2.shape)
HHP3=D3['hhp']; print(HHP3.shape)
print(HHP1.time_counter[0])
print(HHP1.time_counter[-1])

HHP1=D1['hhp'].mean(axis=0)
HHP2=D2['hhp'].mean(axis=0)
HHP3=D3['hhp'].mean(axis=0)

SHHP=D1['hhp'].std(axis=0)

DHHP=HHP1-HHP2
EHHP=HHP2-HHP3
FHHP=HHP1-HHP3
RAT1=np.zeros(HHP1.shape)
RAT2=np.zeros(HHP1.shape)
RAS1=np.zeros(HHP1.shape)
RAS2=np.zeros(HHP1.shape)
RAR1=np.zeros(HHP1.shape)
RAR2=np.zeros(HHP1.shape)
isfin = np.where(HHP2.values > 0)
RAT1[isfin]=DHHP.values[isfin]/HHP2.values[isfin]
RAS1[isfin]=EHHP.values[isfin]/HHP2.values[isfin]
RAR1[isfin]=FHHP.values[isfin]/HHP2.values[isfin]
isfin = np.where(SHHP.values > 0)
RAT2[isfin]=DHHP.values[isfin]/SHHP.values[isfin]
RAS2[isfin]=EHHP.values[isfin]/SHHP.values[isfin]
RAR2[isfin]=FHHP.values[isfin]/SHHP.values[isfin]

box=[-180, 180, -45, 45]
lon=HHP1.nav_lon
lat=HHP1.nav_lat

levels=np.arange(-0.2,0.21,0.01); ticks=np.arange(-0.2,0.225,0.05)
loness=np.arange(-0.95,1.0,0.1);  tones=np.arange(-1.0,1.2,0.2)
cmap = 'seismic'
cplot.grd_pcolormesh(lon.values, lat.values, DHHP.values/1e9, levels=levels, ticks=ticks, outfile='PLOTS_noUS/dhhp_JJASO.png', box=box, title='TCHP difference', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAT1, levels=loness, ticks=tones, outfile='PLOTS_noUS/r1hhp_JJASO.png', box=box, title='TCHP ratio difference/mean', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAT2, levels=loness, ticks=tones, outfile='PLOTS_noUS/r2hhp_JJASO.png', box=box, title='TCHP ratio difference/std', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)

cplot.grd_pcolormesh(lon.values, lat.values, EHHP.values/1e9, levels=levels, ticks=ticks, outfile='PLOTS_noUS/ehhp_JJASO.png', box=box, title='TCHP additonal difference', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAS1, levels=loness, ticks=tones, outfile='PLOTS_noUS/s1hhp_JJASO.png', box=box, title='TCHP ratio additional difference/mean', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAS2, levels=loness, ticks=tones, outfile='PLOTS_noUS/s2hhp_JJASO.png', box=box, title='TCHP ratio additional difference/std', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)

cplot.grd_pcolormesh(lon.values, lat.values, FHHP.values/1e9, levels=levels, ticks=ticks, outfile='PLOTS_noUS/fhhp_JJASO.png', box=box, title='TCHP no Argo difference', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAR1, levels=loness, ticks=tones, outfile='PLOTS_noUS/t1hhp_JJASO.png', box=box, title='TCHP ratio No Argo difference/mean', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, RAR2, levels=loness, ticks=tones, outfile='PLOTS_noUS/t2hhp_JJASO.png', box=box, title='TCHP ratio No Argo difference/std', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)

cmap='gist_stern_r'
levels=np.arange(0,2.1,0.1); ticks=np.arange(0, 2.5, 0.5)

cplot.grd_pcolormesh(lon.values, lat.values, HHP1.values.flatten()/1e9, levels=None, ticks=None, outfile='PLOTS_noUS/hhp1_JJASO.png', box=box, make_global=False, title='TCHP ALL Argo', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, HHP2.values.flatten()/1e9, levels=None, ticks=None, outfile='PLOTS_noUS/hhp2_JJASO.png', box=box, make_global=False, title='TCHP No US ARGO', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, HHP3.values.flatten()/1e9, levels=None, ticks=None, outfile='PLOTS_noUS/hhp3_JJASO.png', box=box, make_global=False, title='TCHP No Argo', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
cplot.grd_pcolormesh(lon.values, lat.values, SHHP.values.flatten()/1e9, levels=None, ticks=None, outfile='PLOTS_noUS/shhp_JJASO.png', box=box, make_global=False, title='TCHP STD', add_gridlines=True, project='PacificCarree', obar='horizontal', cmap=cmap)
