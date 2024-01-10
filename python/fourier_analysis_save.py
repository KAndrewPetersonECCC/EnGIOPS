from importlib import reload
import sys
this_dir='/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python'
sys.path.insert(0, this_dir)

import matplotlib.pyplot as plt
import datetime
import numpy as np


import fft_giops
import read_dia
import check_date
import rank_histogram

hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

BOX_TROP = [ [-175, -10], [-125, -10], [-125, 10], [-175, 10], [-175, -10]]

def cycle_lon(lons):
    clons = (lons+180)%360 - 180
    return clons
    
testdate=check_date.check_date(20220601, outtype=datetime.datetime)
lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', testdate, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
MTFLD = sum(ETFLD)/len(ETFLD)

gdx = 25.0 #km
LLGRID, BOX = fft_giops.create_box( (-172,0), size=2000.0, dx=gdx, theta=0.0 )
#LLGRID, BOX = fft_giops.create_rectangle( (-175, -15.361794886583663/2.0), size_x=2000.0, size_y=2000.0, dx=gdx, dy=gdx, theta=0.0 )
fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[BOX])
MT_box = fft_giops.interpolate_to_box( MTFLD, (lone, late), LLGRID)
ps_MT, fft_MT = fft_giops.get_fft_ps(MT_box)
N=0; 
Nx, Ny = ps_MT.shape; 
if ( Nx == Ny ): N=Nx
wavenumber = 2*np.pi * np.fft.fftfreq(N, gdx)  # actually sampling frequency (so mult by 2pi for k)
L = int((N-1)/2)




LLGRID, BOX = fft_giops.create_rectangle( (150, 35.0), size_x=7000.0, size_y=500.0, dx=gdx, dy=gdx, theta=0.0 )
fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[BOX])
              
lons1, lats1, PTS1 = fft_giops.lat_line(0, 175, gdx, 10000.)
cons1 = cycle_lon(lons1)

lons2, lats2, PTS2 = fft_giops.lon_line(0, -65, gdx, 7500.)
cons2 = cycle_lon(lons2)

lons3, lats3, PTS3 = fft_giops.lat_line(-50, -50, gdx, 5000.)
cons3 = cycle_lon(lons3)


fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[PTS1, PTS2, PTS3])

FLD_line1 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons1, lats1), method='linear')
FLD_line2 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons2, lats2), method='linear')
FLD_line3 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons3, lats3), method='linear')

FLD_line=FLD_line3
lats=lats3; lons=cons3

FLD_FFT = np.fft.fft(FLD_line)
FLD_PSD = FLD_FFT * np.conj(FLD_FFT) 

EFLD_FFT = []
EFLD_PSD = []
for eTFLD in ETFLD:
    eFLD_line = fft_giops.interpolate_to_box(eTFLD[0,0,:,:], (lone, late), (lons, lats), method='linear')
    eFLD_FFT = np.fft.fft(eFLD_line)
    eFLD_PSD = eFLD_FFT * np.conj(eFLD_FFT) 
    EFLD_FFT.append(eFLD_FFT)
    EFLD_PSD.append(eFLD_PSD)

MFLD_FFT = sum(EFLD_FFT) / len(EFLD_FFT)
MFLD_PSD = sum(EFLD_PSD) / len(EFLD_PSD)
    
N = len(FLD_PSD)
wavenumber = 2*np.pi * np.fft.fftfreq(N, gdx)  # actually sampling frequency (so mult by 2pi for k)
L = int((N-1)/2)

plt.loglog(2*np.pi/wavenumber[1:L+1], FLD_PSD[1:L+1], color='b')
plt.loglog(2*np.pi/wavenumber[1:L+1], MFLD_PSD[1:L+1], color='r')
plt.savefig('psd.png')
plt.close()

plt.loglog(2*np.pi/wavenumber[1:L+1], FLD_PSD[1:L+1]/MFLD_PSD[1:L+1], color='k')
plt.savefig('rpsd.png')
plt.close()

CEARTH=40000
GDX=2500
gdx = 25.0 #km

BOXES=[]
GRIDS=[]
for LAT in np.arange(-72, 72, 16):
    NBOX =  np.floor(CEARTH * np.cos(np.deg2rad(LAT+8)) / GDX).astype(int)
    LONS = np.arange(NBOX) * (360.0/NBOX) - 180
    for LON in LONS:
        LLGRID, BOX =  fft_giops.create_box( (LON,LAT), size=2000.0, dx=gdx, theta=0.0 )
        BOXES.append( BOX )
        GRIDS.append( LLGRID )

fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=BOXES)

LLGRID, BOX = fft_giops.create_box( (-172,0), size=2000.0, dx=gdx, theta=0.0 )
FLD_BOX = fft_giops.interpolate_to_box_with_mask(MTFLD[0,0,:,:], (lone, late), LLGRID, method='2sweep')
PSD, FFT = fft_giops.get_fft_ps(FLD_BOX)
Nx, Ny = PSD.shape; N=0
if ( Nx == Ny ): N=Nx

knorm = fft_giops.find_wavenumber_norm(N, gdx)
kbins, kvals = fft_giops.setup_Kbins(N, gdx)

Abins, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean",bins = kbins)   # Note:  Mean can be used as count will be same for given grid.  
Acnts, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "count",bins = kbins)

testdate=check_date.check_date(20220525, outtype=datetime.datetime)
lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', testdate, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
MTFLD = sum(ETFLD)/len(ETFLD)
Abins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean",bins = kbins)
Acnts_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "count",bins = kbins)

Abins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
dates=rank_histogram.create_dates(20220105, 20220601,7)

for date in dates:
    print(date)
    lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', date, fld='SST', file_pre='ORCA025-CMC-ANAL_1d_')
    ESST = [ eTFLD[0,0,:,:] for eTFLD in ETFLD]
    MSST = sum(ESST)/len(ESST)
    SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, (lone, late), LLGRID, method='2sweep')
    PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
    Abins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean",bins = kbins)
    Abins = Abins+Abins_add
    
fig, ax = plt.subplots()
ax.loglog(2*np.pi/kvals, Abins)
ax.set_xlabel("$lambda$")
ax.set_ylabel("$P(k)$")
fig.tight_layout()
fig.savefig("PSD_loglog.png", dpi = 300, bbox_inches = "tight")
plt.close(fig)
    
    
