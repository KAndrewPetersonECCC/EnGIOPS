#from importlib import reload
import sys
this_dir='/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python'
sys.path.insert(0, this_dir)

import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import matplotlib.image as image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)

import datetime
import numpy as np
import scipy.stats
import subprocess
import glob
import os
import time


import fft_giops
import read_dia
import check_date
import rank_histogram
import read_grid
import isoheatcontent
import write_nc_grid
import ctile
import find_hall
import shapiro

hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

#https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts#Superscripts_and_subscripts_block
udeg='\u00b0'
su2='\u00b2'
su3='\u00b3'
su4='\u2074'
su5='\u2075'
supminus='\u207B'
supplus='\u207A'
udot="\u2022"
udot="\u22C5"
hdot2="\u22c5"
hdot3="\u02D9"
hdot4="\u2219"
hdots=[udot, hdot2, hdot3, hdot4]
#for hdot in hdots:
#    print("k"+su4+hdot+su5)
hdot=hdot3    

imgkm3 = image.imread('/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/TexPapers/TexEnGIOPS/GRL/km3.png')
imgkm4p5 = image.imread('/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/TexPapers/TexEnGIOPS/GRL/km4p5.png')
    
def inverse(x):
    """Vectorized 1/x, treating x==0 manually"""
    x = np.array(x, float)
    near_zero = np.isclose(x, 0)
    x[near_zero] = np.inf
    x[~near_zero] = 1 / x[~near_zero]
    return x

def forlog(x):
    y = np.log10(inverse(x))
    return y
    
def baclog(x):
    y = inverse(10**x)
    return y
    
def convert_xticks(xticks, thisfunction=inverse):
    new_xticks = thisfunction(xticks)
    new_xlabels = [ str(xtick) for xtick in new_xticks ]
    return new_xlabels
    
def adjust_xaxis(taxe, logrange=np.array([1,3])):
    if ( isinstance(logrange, list) ): logrange = np.array(logrange)
    alogrange = np.arange(logrange[0], logrange[1]+1)
    blogrange = np.arange(logrange[0], logrange[1])
    logrmin = logrange[0]
    logrmax = logrange[1]
    e10range = 10**logrange
    e10rmin = 10**logrmin
    e10rmax = 10**logrmax
    #taxe.set_xscale('function', functions=(forlog, baclog))
    taxe.xaxis.set_major_formatter(tk.NullFormatter())
    taxe.xaxis.set_minor_formatter(tk.NullFormatter())
    taxe.set_xlim(inverse(np.flip(10**logrange)))
    taxe.set_xticks(inverse(np.flip(10**alogrange)))
    taxe.set_xticks(np.flip(inverse(np.concatenate([np.arange(2,10)*10**(1*ii) for ii in blogrange]))), minor=True)
    Xxticks = taxe.get_xticks()
    Mxticks = taxe.get_xticks(minor=True)
    OldXlabels = taxe.get_xticklabels()
    NewXxticks = inverse(Xxticks)
    NewXlabels = [ str(int(round(xtick))) for xtick in NewXxticks]
    #print(OldXlabels, NewXlabels)
    #print('old labels', taxe.get_xticklabels())
    taxe.set_xticklabels(NewXlabels)
    #print('new labels', taxe.get_xticklabels())
    taxe.set_xlabel('Wavelength')
    return taxe

def special_xaxis(taxe):
    lrange = [40, 1000]
    lmajor=[50, 100, 150, 200, 300, 400, 500, 1000]
    lminor=[40, 60, 70, 80, 90]+list(np.arange(110, 150, 10))+list(np.arange(160, 200, 10))+list(np.arange(210, 300, 10))+[600, 700, 800, 900]
    #taxe.set_xscale('function', functions=(forlog, baclog))
    taxe.xaxis.set_major_formatter(tk.NullFormatter())
    taxe.xaxis.set_minor_formatter(tk.NullFormatter())
    taxe.set_xlim(inverse(np.flip(lrange)))
    taxe.set_xticks(inverse(np.flip(lmajor)))
    taxe.set_xticks(np.flip(inverse(lminor)), minor=True)
    Xxticks = taxe.get_xticks()
    Mxticks = taxe.get_xticks(minor=True)
    OldXlabels = taxe.get_xticklabels()
    NewXxticks = inverse(Xxticks)
    NewXlabels = [ str(int(round(xtick))) for xtick in NewXxticks]
    #print(OldXlabels, NewXlabels)
    #print('old labels', taxe.get_xticklabels())
    taxe.set_xticklabels(NewXlabels)
    #print('new labels', taxe.get_xticklabels())
    taxe.set_xlabel('Wavelength')
    return taxe

def cycle_lon(lons):
    clons = (lons+180)%360 - 180
    return clons

def read_test_fld(var='T'):
    testdate=check_date.check_date(20220601, outtype=datetime.datetime)
    lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', testdate, fld=var, file_pre='ORCA025-CMC-ANAL_1d_')
    MTFLD = sum(ETFLD)/len(ETFLD)
    return lone, late, ETFLD, MTFLD

def test1():  
    lone, late, ETFLD, MTFLD = read_test_fld()

    gdx = 25.0 #km
    LLGRID, BOX = fft_giops.create_box( (-172,0), size=2000.0, dx=gdx, theta=0.0 )
    fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[BOX])
    MT_box = fft_giops.interpolate_to_box( MTFLD, (lone, late), LLGRID)
    ps_MT, fft_MT = fft_giops.get_fft_ps(MT_box)
    N=0; 
    Nx, Ny = ps_MT.shape; 
    L = int((N-1)/2)

    lons1, lats1, PTS1 = fft_giops.lat_line(0, 175, gdx, 10000  )
    cons1 = cycle_lon(lons1)

    lons2, lats2, PTS2 = fft_giops.lon_line(0, -65, gdx, 7500.)
    cons2 = cycle_lon(lons2)

    lons3, lats3, PTS3 = fft_giops.lat_line(-50, -50, gdx, 5000.)
    cons3 = cycle_lon(lons3)


    fft_giops.pcolormesh_with_box(lone, late, MTFLD[0,0,:,:], levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[PTS1, PTS2, PTS3], outfile='lines.png')

    FLD_line1 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons1, lats1), method='linear')
    FLD_line2 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons2, lats2), method='linear')
    FLD_line3 = fft_giops.interpolate_to_box(MTFLD[0,0,:,:], (lone, late), (cons3, lats3), method='linear')

    FLD_line=FLD_line3
    lats=lats3; lons=cons3

    FLD_FFT = np.fft.fft(FLD_line)
    FLD_PSD = np.abs(FLD_FFT * np.conj(FLD_FFT)) 

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
    wavenumber = np.fft.fftfreq(N, gdx)  # actually sampling frequency (so mult by 2pi for k)
    L = int((N-1)/2)

    plt.loglog(1.0/wavenumber[1:L+1], FLD_PSD[1:L+1], color='b')
    plt.loglog(1.0/wavenumber[1:L+1], MFLD_PSD[1:L+1], color='r')
    plt.savefig('psd.png')
    plt.close()

    plt.loglog(1.0/wavenumber[1:L+1], FLD_PSD[1:L+1]/MFLD_PSD[1:L+1], color='k')
    plt.savefig('rpsd.png')
    plt.close()
    return

BOX_DNFO = { 'gdx' : 20.0, 'GDX': 1000, 'threshold' : 0.95}
def create_BOXES(gdx=BOX_DNFO['gdx'], GDX=BOX_DNFO['GDX'], threshold=BOX_DNFO['threshold']):
    CEARTH=40000
    #GDX=2500.0 #km
    #gdx = 25.0 #km

    mask = read_grid.read_mask(var='tmask')
    sask = np.squeeze(mask)[0,:,:]

    lone, late, ETFLD, MTFLD = read_test_fld()
    TSURF=MTFLD[0,0,:,:]

    BOXES=[]
    GRIDS=[]
    LATL = CEARTH / 2 / 180
    LATT = LATL * (80+84)
    NBOX =  np.floor(LATT / GDX).astype(int)
    LATS = np.arange(NBOX) * (80.0+84) / NBOX - 80
    #print(LATS)
    #LATS = LATS[1:-1]
    #print(LATS)
    for LAT in LATS:
        NBOX =  np.floor(CEARTH * np.cos(np.deg2rad(LAT+8)) / GDX).astype(int)
        LONS = np.arange(NBOX) * (360.0/NBOX) - 180
        for LON in LONS:
            LLGRID, BOX =  fft_giops.create_box( (LON,LAT), size=GDX, dx=gdx, theta=0.0 )
            BOXES.append( BOX )
            GRIDS.append( LLGRID )
    fft_giops.pcolormesh_with_box(lone, late, TSURF, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=BOXES, outfile='Boxes.png')
    print('Number of BOXES', len(BOXES))    
    NEW_BOXES=[]
    NEW_GRIDS=[]

    iib = 0
    for ib, BOX in enumerate(BOXES):
        LLGRID = GRIDS[ib]
        MSK_BOX = fft_giops.interpolate_to_box(sask, (lone, late), LLGRID, method='nearest')
        avg_BOX = np.mean(MSK_BOX)
        TorF = ( avg_BOX > threshold )
        #print(ib, TorF)
        if ( TorF ) :
            iib = iib+1
            NEW_BOXES.append(BOX)
            NEW_GRIDS.append(LLGRID)
    BTEXT = [ str(ibox).zfill(3) for ibox in range(len(NEW_BOXES))]
    BLOCO = [ BOX[0] for BOX in NEW_BOXES ]    
    fft_giops.pcolormesh_with_box(lone, late, TSURF, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=NEW_BOXES, plot_text=BTEXT, loco_text=BLOCO, outfile='Soxes.png')
    print('Number of BOXES', len(NEW_BOXES))    
    return NEW_BOXES, NEW_GRIDS, LATS

#fourier_analysis.test_cycle(dates=rank_histogram.create_dates(20210609, 20210630,7), var='SST', GDX=900, gdx=10, LL_SW=(-165, 72) )  # Beaufort Sea for Charlie.
def read_field(expt, date, var, ddir=mir5, file_pre='ORCA025-CMC-ANAL_1d_'):
    date = check_date.check_date(date, outtype=datetime.datetime)
    if ( var == 'D20' ):
        lone, late, ETFLD = read_dia.read_ensemble(ddir, 'GIOPS_T', date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
    elif ( ( var == 'R75' ) or  ( var == 'R3C' ) ):
        lone, late, ETFLD = read_dia.read_ensemble(ddir, 'GIOPS_T', date, fld='SST', file_pre='ORCA025-CMC-ANAL_1d_')
        nx, ny = np.squeeze(ETFLD[0]).shape
        ETFLD = [ np.random.randn(nx,ny) for eTFLD in ETFLD ]
    else:
        lone, late, ETFLD = read_dia.read_ensemble(ddir, 'GIOPS_T', date, fld=var, file_pre='ORCA025-CMC-ANAL_1d_')
    ESST = [ np.squeeze(eTFLD/1) for eTFLD in ETFLD]
    if ( var == 'T' ):
        level=22
        ESST = [ np.squeeze(eSST[level,:,:]/1) for eSST in ESST]
        deptht=read_dia.read_sam2_levels()
        print('Subsetting to ', deptht[level])
    if ( var[1:] == 'sppt' ):
       level=2
       ESST = [ np.squeeze(eSST[level,:,:]/1) for eSST in ESST[1:]]
       deptht=read_dia.read_sam2_levels()
       print('Subsetting to ', deptht[level])
       print('Removed ENS 0')
    ne = len(ESST)
    if ( var == 'D20' ):
        NSST = []
        bottom=read_grid.bottom_depth_mesh()
        deptht=read_dia.read_sam2_levels()
        for eSST in ESST:
           D_iso = isoheatcontent.isotherm(eSST.data, tmask, deptht, bottom, Tlevel=20)
           D_msk = np.ma.array(D_iso, mask=(1-tmask[0,:,:]).astype(bool))
           NSST.append(D_msk)
        ESST=NSST
    if ( var == 'R75' ):
        time0=time.time()
        ESST = [ call_shapiro(eSST, 75) for eSST in ESST ]
        time_elapsed = time.time() - time0
        print('Finished SHAPIRO after ', time_elapsed)
    if ( var == 'R3C' ):
        time0=time.time()
        ESST = [ call_shapiro(eSST, 300) for eSST in ESST ]
        time_elapsed = time.time() - time0
        print('Finished SHAPIRO after ', time_elapsed)
    MSST = sum(ESST)/ne
    return MSST, ESST, (lone, late)

def call_shapiro(fld, npass):
    Ffld, __ = shapiro.shapiro2D(fld, npass=npass)
    return Ffld    

def test_cycle(dates=rank_histogram.create_dates(20210609, 20220601,7), var='SST', gdx=25.0, GDX=2500, LL_SW=(-172, 0) ):
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    LLGRID, BOX = fft_giops.create_box( LL_SW, size=GDX, dx=gdx, theta=0.0 )
    print('BOX', BOX)
    Nx, Ny = LLGRID[0].shape
    if ( Nx == Ny ): N=Nx

    knorm, kwave = fft_giops.find_wavenumber_norm(N, gdx)
    kbins, kvals = fft_giops.setup_Kbins(N, gdx)

    Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    Ebins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    fig, ax = plt.subplots()
    fir, ar = plt.subplots()
    ndates=len(dates)
    clr = ['r', 'c', 'g', 'b']
    lst = [0, 1, 7, 14]
    nt=len(dates)
    lst = [0, nt-1]
    if ( len(dates) < 5 ):
        lst = list(range(4))
    elif ( len(dates) < 8 ):
        lst = [0, 2, 4, 6]
    elif ( len(dates) < 13 ):
        lst = [0, 4, 8, 12]
    elif ( len(dates) < 26 ):
         lst = [0, 4, 13, 20]
    for idate, date in enumerate(dates):
        print(date)
        MSST = sum(ESST)/ne
        MSST, ESST, (lone, late) = read_field('GIOPS_T', date, var)
        ne = len(ESST)

        if ( idate == 0 ):
           #fft_giops.pcolormesh_with_box(lone, late, MSST, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[BOX], outfile='Box.'+oar+'.png')
           fft_giops.pcolormesh_with_box(lone, late, MSST, levels=None, ticks=None, project='NorthPolarStereo',box=[-180, 180, 60, 90], obar='horizontal', plot_boxes=[BOX], outfile='Box.'+oar+'.png')
        SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, (lone, late), LLGRID, method='nearest')
        PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
        kw, PSW = fft_giops.get_welch_psd(SST_BOX)
        Mbins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
        Mbins = Mbins+Mbins_add
        PSE = np.zeros(PSD)
        for eSST in ESST:
            SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, (lone, late), LLGRID, method='nearest')
            PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
            kw, PSW = fft_giops.get_welch_psd(SST_BOX)
            PSE = PSE + PSW/ne
            Ebins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
            Ebins = Ebins+Ebins_add/ne
        if ( idate in lst ):
            print(idate, lst.index(idate))
            ax.loglog(1.0/kvals, Mbins/(idate+1), linestyle='-', color=clr[lst.index(idate)], label=str(idate))
            ax.loglog(1.0/kvals, Ebins/(idate+1), linestyle='--', color=clr[lst.index(idate)], label=str(idate))
            ar.semilogx(1.0/kvals, Mbins/Ebins, linestyle='-', color=clr[lst.index(idate)], label=str(idate))
    ax.loglog(1.0/kvals, Mbins/nt, linestyle='-', color='k', label=str(nt))
    ax.loglog(1.0/kvals, Ebins/nt, linestyle='--', color='k', label=str(nt))
    ar.semilogx(1.0/kvals, Mbins/Ebins, linestyle='-', color='k', label=str(nt))
    ax.legend()
    ax.set_xlabel("$lambda$")
    ax.set_ylabel("$P(k)$")
    fig.tight_layout()
    fig.savefig("PSD_loglog."+oar+".png", dpi = 300, bbox_inches = "tight")
    plt.close(fig)
    ar.legend()
    ar.set_xlabel("$lambda$")
    ar.set_ylabel("Ratio")
    fir.tight_layout()
    fir.savefig("PSD_ratio."+oar+".png", dpi = 300, bbox_inches = "tight")
    plt.close(fir)
    return

# Suspect I will not be able to cycle both dates and boxes.  Get them working first -- and then we will likely need intermediate output.   

def box_cycle_orig(date=datetime.datetime(2021,6,2), var='SST', BOX_INFO=BOX_DNFO):
    datestr = check_date.check_date(date, outtype=str)
    outdir='BOX_'+datestr+'/'
    rc=subprocess.call(['mkdir', outdir])
    BOXES, GRIDS, LATS = create_BOXES(gdx=BOX_INFO['gdx'], GDX=BOX_INFO['GDX'], threshold=BOX_INFO['threshold'])
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    GDX=1000.0 #km 
    gdx = 20.0 #km
    #LLGRID, BOX = fft_giops.create_box( (-172,0), size=GDX, dx=gdx, theta=0.0 )
    nbox = len(BOXES)
    print('NUMBER OF BOXES', nbox)

    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx
    npsd = int((N+1)/2)

    #knorm, kwave = fft_giops.find_wavenumber_norm(N, gdx)
    #kwave = kwave[:npsd]
    #kbins, kvals = fft_giops.setup_Kbins(N, gdx)
    
    kwave = fft_giops.find_wavenumber(N,gdx)
    kwave = kwave[:npsd]
    

    #Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    #Ebins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    lats = [-70, -55, -35]
    clr = ['r', 'c', 'g', 'b', 'm']
    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    ncol=len(clr)

    MSST, ESST, (lone, late) = read_field('GIOPS_T', date, var)
    ne = len(ESST)

    fft_giops.pcolormesh_with_box(lone, late, MSST, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=BOXES, outfile=outdir+oar+'.png')
    #Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    #Ebins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    #fig, ax = plt.subplots()
    #fir, ar = plt.subplots()
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    lcol = -1
    #Mbins_list = []
    #Ebins_list = []
    PSM_list = []
    PSE_list = []
    PSA = np.zeros(npsd)
    PSB = np.zeros(npsd)
    for ibox, BOX in enumerate(BOXES):
        print(ibox, nbox, BOX)
        lat = BOX[0][1]
        icol = 0
        for ii, LAT in enumerate(LATS):
            if ( lat > LAT-1 ): icol=ii
        #big, bax = plt.subplots()
        #bir, bar = plt.subplots()
        #cig, cax = plt.subplots()
        #cir, car = plt.subplots()
        LLGRID = GRIDS[ibox]
        SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, (lone, late), LLGRID, method='nearest')
        #PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
        KW, PSM = fft_giops.get_welch_psd(SST_BOX)
        #Mbins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
        #Mbins = Mbins+Mbins_add/nbox
        PSA = PSA + PSM / nbox
        #Ebins_add, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
        PSE = np.zeros(npsd)
        for eSST in ESST:
            SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, (lone, late), LLGRID, method='nearest')
            #PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
            kw, PSW = fft_giops.get_welch_psd(SST_BOX)
            PSE = PSE + PSW/ne
            #Ebins_edd, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
            #Ebins_add = Ebins_add+Ebins_edd/ne
        #Ebins = Ebins+Ebins_add/nbox
        PSB = PSB+PSE/nbox
        if ( lcol < icol ): 
            lcol=icol
            #ax.loglog(1.0/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            #ar.semilogx(1.0/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
        else:
            #ax.loglog(1.0/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol])
            #ar.semilogx(1.0/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol])
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol])
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol])
        #ax.loglog(1.0/kvals, Ebins_add, linestyle='--', color=clr[icol%ncol])
        bx.loglog(1.0/kwave[1:], PSE[1:], linestyle='--', color=clr[icol%ncol])
        #bax.loglog(1.0/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol], label='Ensemble Mean')
        #bax.loglog(1.0/kvals, Ebins_add, linestyle='--', color=clr[icol%ncol], label='Mean Ensemble')
        #cax.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol], label='Ensemble Mean')
        #cax.loglog(1.0/kwave[1:], PSE[1:], linestyle='--', color=clr[icol%ncol], label='Mean Ensemble')
        #bar.semilogx(1.0/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol], label=str(ibox))
        #car.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol], label=str(ibox))
        #bax.legend()
        #cax.legend()
        crstr = '('+str(BOX[0][0])+'E, '+ str(BOX[0][1])+'N)'
        #bax.set_title('PSD Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        #bax.set_xlabel("$lambda$")
        #bax.set_ylabel("$P(k)$")
        #cax.set_title('Welch PSD Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        #cax.set_xlabel("$lambda$")
        #cax.set_ylabel("$P(k)$")
        #big.tight_layout()
        #big.savefig(outdir+"GPSD_loglog."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        #cig.tight_layout()
        #cig.savefig(outdir+"GPSW_loglog."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        #plt.close(big)
        #plt.close(cig)
        #bar.set_title('Ratio Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        #bar.set_xlabel("$lambda$")
        #bar.set_ylabel("Ratio")
        #car.set_title('Welch Ratio Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        #car.set_xlabel("$lambda$")
        #car.set_ylabel("Ratio")
        #bir.tight_layout()
        #bir.savefig(outdir+"PSD_ratio."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        #plt.close(bir)
        #cir.tight_layout()
        #cir.savefig(outdir+"PSW_ratio."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        #plt.close(cir)
        #Mbins_list.append(Mbins_add)
        #Ebins_list.append(Ebins_add)
        PSM_list.append(PSM)
        PSE_list.append(PSE)
    #ax.loglog(1.0/kvals, Mbins, linestyle='-', color='k', label='Global Mean')
    #ax.loglog(1.0/kvals, Ebins, linestyle='--', color='k')
    #ar.semilogx(1.0/kvals, Mbins/Ebins, linestyle='-', color='k', label='Global Mean')
    #ax.legend()
    #ax.set_xlabel("$lambda$")
    #ax.set_ylabel("$P(k)$")
    #fig.tight_layout()
    #fig.savefig(outdir+"PSD_loglog."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    #plt.close(fig)
    #ar.legend()
    #ar.set_xlabel("$lambda$")
    #ar.set_ylabel("Ratio")
    #fir.tight_layout()
    #fir.savefig(outdir+"PSD_ratio."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    #plt.close(fir)
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)
    #fig, ax = plt.subplots()
    #fir, ar = plt.subplots()
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    #ax.loglog(1.0/kvals, Mbins, linestyle='-', color='k', label='Ensemble Mean')
    #ax.loglog(1.0/kvals, Ebins, linestyle='--', color='k', label='Mean Ensemble Members')
    #ar.semilogx(1.0/kvals, Mbins/Ebins, linestyle='-', color='k', label='Ratio')
    #ax.legend()
    #ax.set_xlabel("$lambda$")
    #ax.set_ylabel("$P(k)$")
    #fig.tight_layout()
    #fig.savefig(outdir+"PSD_loglog."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    #plt.close(fig)
    #ar.legend()
    #ar.set_xlabel("$lambda$")
    #ar.set_ylabel("Ratio")
    #fir.tight_layout()
    #fir.savefig(outdir+"PSD_ratio."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    #plt.close(fir)
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)

    PSA_fulllist = [PSA]+PSM_list 
    PSB_fulllist = [PSB]+PSE_list
    PSA_array = np.array(PSA_fulllist)
    PSB_array = np.array(PSB_fulllist)
    print(PSA_array.shape)
    print(PSB_array.shape)
    write_nc_grid.write_nc_1d([kwave, PSA_array, PSB_array], ['kwave', 'psd_mean', 'psd_member'], 'BOX.O/'+var+'_psd_'+datestr+'.nc')
   
    #return kvals, Mbins, Ebins, Mbins_list, Ebins_list   
    return kwave, PSA_fulllist, PSB_fulllist

def box_cycle(date=datetime.datetime(2021,6,2), var='SST', BOX_INFO=BOX_DNFO, method='nearest'):
    datestr = check_date.check_date(date, outtype=str)
    outdir='BOX.S_'+datestr+'/'
    rc=subprocess.call(['mkdir', outdir])
    BOXES, GRIDS, LATS = create_BOXES(gdx=BOX_INFO['gdx'], GDX=BOX_INFO['GDX'], threshold=BOX_INFO['threshold'])
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    GDX=1000.0 #km 
    gdx = 20.0 #km
    #LLGRID, BOX = fft_giops.create_box( (-172,0), size=GDX, dx=gdx, theta=0.0 )
    nbox = len(BOXES)
    print('NUMBER OF BOXES', nbox)

    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx
    npsd = int((N+1)/2)

    kwave = fft_giops.find_wavenumber(N,gdx)
    kwave = kwave[:npsd]
    
    lats = [-70, -55, -35]
    clr = ['r', 'c', 'g', 'b', 'm']
    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    ncol=len(clr)

    MSST, ESST, LONLAT = read_field('GIOPS_T', date, var)
    ne = len(ESST)

    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    lcol = -1
    PSM_list = []
    PSE_list = []
    PSA = np.zeros(npsd)
    PSB = np.zeros(npsd)
    for ibox, BOX in enumerate(BOXES):
        print(ibox, nbox, BOX)
        lat = BOX[0][1]
        icol = 0
        for ii, LAT in enumerate(LATS):
            if ( lat > LAT-1 ): icol=ii
        LLGRID = GRIDS[ibox]
        # method needs to be 'nearest' for all boxes to complete -- or use cycle_box_fast!
        SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, LONLAT, LLGRID, method=method)
        KW, PSM = fft_giops.get_welch_psd(SST_BOX)
        PSA = PSA + PSM / nbox
        PSE = np.zeros(npsd)
        for eSST in ESST:
            SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, LONLAT, LLGRID, method=method)
            kw, PSW = fft_giops.get_welch_psd(SST_BOX)
            PSE = PSE + PSW/ne
        PSB = PSB+PSE/nbox
        if ( lcol < icol ): 
            lcol=icol
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
        else:
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol])
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol])
        bx.loglog(1.0/kwave[1:], PSE[1:], linestyle='--', color=clr[icol%ncol])
        crstr = '('+str(BOX[0][0])+'E, '+ str(BOX[0][1])+'N)'
        PSM_list.append(PSM)
        PSE_list.append(PSE)
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)

    PSA_fulllist = [PSA]+PSM_list 
    PSB_fulllist = [PSB]+PSE_list
    PSA_array = np.array(PSA_fulllist)
    PSB_array = np.array(PSB_fulllist)
    print(PSA_array.shape)
    print(PSB_array.shape)
    write_nc_grid.write_nc_1d([kwave, PSA_array, PSB_array], ['kwave', 'psd_mean', 'psd_member'], 'BOX.S/'+var+'_psd_'+datestr+'.nc')
   
    return kwave, PSA_fulllist, PSB_fulllist

def box_cycle_fast(date=datetime.datetime(2021,6,2), var='SST', BOX_INFO=BOX_DNFO, method='2sweep'):
    datestr = check_date.check_date(date, outtype=str)
    outdir='BOX_'+datestr+'/'
    rc=subprocess.call(['mkdir', outdir])
    BOXES, GRIDS, LATS = create_BOXES(gdx=BOX_INFO['gdx'], GDX=BOX_INFO['GDX'], threshold=BOX_INFO['threshold'])
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    GDX=1000.0 #km 
    gdx = 20.0 #km
    #LLGRID, BOX = fft_giops.create_box( (-172,0), size=GDX, dx=gdx, theta=0.0 )
    nbox = len(BOXES)
    print('NUMBER OF BOXES', nbox)

    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx
    npsd = int((N+1)/2)

    kwave = fft_giops.find_wavenumber(N,gdx)
    kwave = kwave[:npsd]
    
    lats = [-70, -55, -35]
    clr = ['r', 'c', 'g', 'b', 'm']
    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    ncol=len(clr)
    
    MSST, ESST, LONLAT = read_field('GIOPS_T', date, var)
    ne = len(ESST)
    
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    lcol = -1
    PSM_list = []
    PSE_list = []
    PSA = np.zeros(npsd)
    PSB = np.zeros(npsd)

    print('PERFORMING INTERPOLATION')
    SST_BOXES = fft_giops.interpolate_to_boxes(MSST, LONLAT, GRIDS, method=method)
    SST_EBOXES = []
    for eSST in ESST:
        SST_eBOXES = fft_giops.interpolate_to_boxes(eSST, LONLAT, GRIDS, method=method)
        SST_EBOXES.append(SST_eBOXES)

    print('PERFORMING PSD')
    for ibox, BOX in enumerate(BOXES):
        print(ibox, nbox, BOX)
        lat = BOX[0][1]
        icol = 0
        for ii, LAT in enumerate(LATS):
            if ( lat > LAT-1 ): icol=ii
        LLGRID = GRIDS[ibox]
        SST_BOX = SST_BOXES[ibox]
        KW, PSM = fft_giops.get_welch_psd(SST_BOX)
        PSA = PSA + PSM / nbox
        PSE = np.zeros(npsd)
        for ie, eSST in enumerate(ESST):
            SST_BOX = SST_EBOXES[ie][ibox]
            #SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, LONLAT, LLGRID, method='linear')
            kw, PSW = fft_giops.get_welch_psd(SST_BOX)
            PSE = PSE + PSW/ne
        PSB = PSB+PSE/nbox
        if ( lcol < icol ): 
            lcol=icol
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
        else:
            bx.loglog(1.0/kwave[1:], PSM[1:], linestyle='-', color=clr[icol%ncol])
            br.semilogx(1.0/kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color=clr[icol%ncol])
        bx.loglog(1.0/kwave[1:], PSE[1:], linestyle='--', color=clr[icol%ncol])
        crstr = '('+str(BOX[0][0])+'E, '+ str(BOX[0][1])+'N)'
        PSM_list.append(PSM)
        PSE_list.append(PSE)
    print('PERFORMING PLOTTING')
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.all'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    bx.loglog(1.0/kwave[1:], PSA[1:], linestyle='-', color='k', label='Global Mean')
    bx.loglog(1.0/kwave[1:], PSB[1:], linestyle='--', color='k')
    br.semilogx(1.0/kwave[1:], PSA[1:]/PSB[1:], linestyle='-', color='k', label='Global Mean')
    bx.legend()
    bx.set_xlabel("$lambda$")
    bx.set_ylabel("$P(k)$")
    gig.tight_layout()
    gig.savefig(outdir+"PSW_loglog."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br.set_xlabel("$lambda$")
    br.set_ylabel("Ratio")
    gir.tight_layout()
    gir.savefig(outdir+"PSW_ratio."+oar+'.glb'+".png", dpi = 300, bbox_inches = "tight")
    plt.close(gir)

    PSA_fulllist = [PSA]+PSM_list 
    PSB_fulllist = [PSB]+PSE_list
    PSA_array = np.array(PSA_fulllist)
    PSB_array = np.array(PSB_fulllist)
    print(PSA_array.shape)
    print(PSB_array.shape)
    write_nc_grid.write_nc_1d([kwave, PSA_array, PSB_array], ['kwave', 'psd_mean', 'psd_member'], 'BOX/'+var+'_psd_'+datestr+'.nc')
   
    return kwave, PSA_fulllist, PSB_fulllist

def cycle_dates_done(date_list, var='U15', BOX_INFO=BOX_DNFO, indir='BOX/', outdir='BOX/'):
    host=find_hall.get_host()
    usetex = False
    if ( host[0:4] == 'hpcr' ):
        usetex=False
    plt.rc('text', usetex=usetex)
    field_id = ''
    units=''
    if ( var == 'K15' or var == 'U15' or var == 'V15' ):  
        field_id = ' velocity '
        units="( (m/s)"+su2+" m )"
        if usetex:  units="( (m/s)$^2 \cdot$ m )"
    if ( var == 'KE0' or var == 'SSU' or var == 'SSV' ):  
        field_id = ' velocity '
        units="( (m/s)"+su2+udot+"m )"
        units="( (m/s)$^2 \cdot$m )"
    if ( var == 'TAUK' ): 
        field_id = ' wind stress '
        units="( (N/m^2)"+su2+udot+"m )"
        if usetex: units="( (N/m$^2$)$^2 \cdot$m )"
    if ( var == 'SST' or var == 'T100' or var == 'T'): 
        field_id = ' temperature '
        units="( (K)"+su2+udot+"m )"
        if usetex: units="( (K)$^2 \cdot$m )"
    if ( var == 'MLD' ): 
        field_id = ' Mixed Layer Depth '
        units="( (m)"+su2+udot+"m )"
        if usetex: units="( (m)$^2 \dot$m )"
            
    if ( isinstance(date_list, type(None)) ):
        invar=var
        if ( var == 'K15' ): invar='U15'
        if ( var == 'KE0' ): invar='SSU'
        if ( var == 'TAUK' ): invar='TAUX'
            
        files=glob.glob(indir+invar+'_psd_'+'????????'+'.nc')
        date_list=[]
        startx=5+len(invar)
        finalx=startx+8
        for file in files:
            date_list.append(os.path.basename(file)[startx:finalx])
        date_list=sorted(date_list)
        print('DATE LIST ', date_list)
    date_list = check_date.check_date_list(date_list, outtype=datetime.datetime)
    BOXES, GRIDS, LATS = create_BOXES(gdx=BOX_INFO['gdx'], GDX=BOX_INFO['GDX'], threshold=BOX_INFO['threshold'])
    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    cl5 = ['g', 'm', 'r', 'c', 'b']
    nclr = len(clr)

    oar=var
    if ( var == 'T' ): oar='T100'
    nbox = len(BOXES)
    print('NUMBER OF BOXES', nbox)

    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx
    npsd = int((N+1)/2)
    print(N, npsd)

    # SMALLEST WAVELENGTH SHUULD BE TWICE THE GRID SPACE.  fftfreq needs to be normalized (N)/(N-1)
    kwave = fft_giops.find_wavenumber(N,BOX_INFO['gdx']) * N / (N-1)
    kwav2 = kwave[:npsd]
    print("SMALLEST WAVELENGTH", 1 / kwav2[-1])
    
    psd_mean_list = []
    psd_memb_list = []
    
    KT05 = []  
    KTMN = []  
    for date in date_list:
        datestr = check_date.check_date(date, outtype=str)
        if ( var == 'K15' ):
          ncfile = indir+'U15'+'_psd_'+datestr+'.nc'
          kwave_date, upsd_mean, upsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          ncfile = indir+'V15'+'_psd_'+datestr+'.nc'
          kwave_date, vpsd_mean, vpsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          psd_mean = 0.5 * (upsd_mean+vpsd_mean)
          psd_memb = 0.5 * (upsd_memb+vpsd_memb)
        elif ( var == 'KE0' ):
          ncfile = indir+'SSU'+'_psd_'+datestr+'.nc'
          kwave_date, upsd_mean, upsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          ncfile = indir+'SSV'+'_psd_'+datestr+'.nc'
          kwave_date, vpsd_mean, vpsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          psd_mean = 0.5 * (upsd_mean+vpsd_mean)
          psd_memb = 0.5 * (upsd_memb+vpsd_memb)
        elif ( var == 'TAUK' ):
          ncfile = indir+'TAUX'+'_psd_'+datestr+'.nc'
          kwave_date, upsd_mean, upsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          ncfile = indir+'TAUY'+'_psd_'+datestr+'.nc'
          kwave_date, vpsd_mean, vpsd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
          psd_mean = 0.5 * (upsd_mean+vpsd_mean)
          psd_memb = 0.5 * (upsd_memb+vpsd_memb)
        else:
          ncfile = indir+var+'_psd_'+datestr+'.nc'
          kwave_date, psd_mean, psd_memb = write_nc_grid.read_nc_1d(ncfile, ['kwave', 'psd_mean', 'psd_member'])
      
        # SMALLEST WAVELENGTH SHUULD BE TWICE THE GRID SPACE.  fftfreq needs to be normalized (N)/(N-1)
        ## REMOVE IFF DONE IN CYCLE_BOX  !!!!!
        kwave_date = kwave_date * N / (N-1)
        print(ncfile)
        print('kwave', kwave, kwav2, kwave_date, np.all(kwave_date == kwave), np.all(kwave_date == kwav2)),
        #print(len(kwave), len(kwav2), len(kwave_date))
        psd_mean_list.append(psd_mean)
        psd_memb_list.append(psd_memb)
        PSM = np.mean(psd_mean, axis=0)
        PSE = np.mean(psd_memb, axis=0)
        RAT = PSM[1:]/PSE[1:]
        i05 = np.where(RAT < 0.5)
        imn = np.argmin(RAT)
        if ( len(i05[0]) > 0 ):
            print(date, len(kwave_date), len(i05[0]), len(RAT), len(PSM), len(PSE), len(PSM[1:]/PSE[1:]), len(PSM/PSE))
            k05 = kwave_date[1:][i05]
            KT05.append(k05[0])
        else:
            KT05.append(kwave_date[0])
        KTMN.append(kwave_date[1:][imn])
        if ( date == date_list[0] ):
            kwave = kwave_date
            print("SMALLEST WAVELENGTH", 1 / kwave[-1])

    print( "LIST LENGTHS", len(psd_mean_list), len(psd_memb_list) )            
    psd_mean = sum(psd_mean_list) / len(psd_mean_list)
    psd_memb = sum(psd_memb_list) / len(psd_memb_list)

    K05 = []  
    KMN = []
    BRT = []
    iLT = [ [] for LAT in LATS]
    #LATP = [-90, -60, -20, 20, 60, 90]
    LATP = [-75, -45, -15, 15, 45, 75]
    nlatp = len(LATP)-1
    jLT = [ [] for LAT in LATP[1:] ]
    for ibox, BOX in enumerate(BOXES):
        lat = BOX[0][1]
        ilat = 0
        for ii, LAT in enumerate(LATS):
            if ( lat >= LAT ): ilat=ii
        print('QUERY', ibox, ilat, len(LATS), lat, LATS)
        iLT[ilat].append(ibox)
        LLGRID = GRIDS[ibox]
        GLON, GLAT = LLGRID
        midLAT = np.mean(GLAT)
        for jj in range(nlatp):
            minLat = LATP[jj]
            maxLat = LATP[jj+1]
            if ( ( minLat < midLAT ) and ( midLAT < maxLat ) ): jLT[jj].append(ibox)
        
        PSM = psd_mean[ibox, :]
        PSE = psd_memb[ibox, :]
        RAT = PSM[1:]/PSE[1:]
        i05 = np.where(RAT < 0.5)
        imn = np.argmin(RAT)
        if ( len(i05[0]) > 0 ):
            k05 = kwave[1:][i05]
            K05.append(k05[0])
        else:
            K05.append(kwave[0])
        KMN.append(kwave[1:][imn])
        BRT.append(RAT[imn])
        

    for ii, LAT in enumerate(LATS):
        print('IQUERY', iLT[ii])
    for jj in range(nlatp):
        print('JQUERY', jLT[jj])
    #print(K05)
    K05 = np.array(K05)
    KMN = np.array(KMN)
    BRT = np.array(BRT)
    PSM = np.mean(psd_mean, axis=0)
    PSE = np.mean(psd_memb, axis=0)
    iPSM = [np.zeros(kwave.shape)]*len(LATS)
    iPSE = [np.zeros(kwave.shape)]*len(LATS)
    iK05 = [0]*len(LATS)
    iKMN = [0]*len(LATS)
    iBRT = [0]*len(LATS)
    iLAT = LATS.copy()
    jPSM = [np.zeros(kwave.shape)]*nlatp
    jPSE = [np.zeros(kwave.shape)]*nlatp
    for ilat, LAT in enumerate(LATS):
      if ( len(iLT[ilat]) > 0 ):   
        iPSM[ilat] = np.mean(psd_mean[iLT[ilat], :], axis=0)
        iPSE[ilat] = np.mean(psd_memb[iLT[ilat], :], axis=0)
        iK05[ilat] = len(iLT[ilat])/sum(K05[iLT[ilat]])  # reciprocate to a wavelength here
        iKMN[ilat] = len(iLT[ilat])/sum(KMN[iLT[ilat]])  # reciprocate to a wavelength here
        iBRT[ilat] = sum(BRT[iLT[ilat]])/len(iLT[ilat])
        iLAT[ilat] = sum([ np.mean(GRIDS[ilt][1]) for ilt in iLT[ilat] ])/len(iLT[ilat])
        #iLAT[ilat] = sum([ np.mean(GRID[1]) for GRID in GRIDS[iLT[ilat]] ])/len(iLT[ilat])
    for jlat in range(nlatp):
      if ( len(jLT[jlat]) > 0 ):   
        jPSM[jlat] = np.mean(psd_mean[jLT[jlat], :], axis=0)
        jPSE[jlat] = np.mean(psd_memb[jLT[jlat], :], axis=0)

    VLAT = []
    VK05 = []
    VKMN = []
    VBRT = []
    for ilat, LAT in enumerate(LATS):
        print(ibox, 'MIDLAT', GLAT, LAT, midLAT)
        if ( len(iLT[ilat]) > 0 ):
            VLAT.append(iLAT[ilat])
            VK05.append(iK05[ilat])
            VKMN.append(iKMN[ilat])
            VBRT.append(iBRT[ilat])
                      
    fig, ax = plt.subplots()
    #ax.plot(date_list, KT05, linestyle='--', label='Ratio = 0.5')
    ax.plot(date_list, KTMN, linestyle='-', label='Minimum Ratio') 
    ax.legend()
    ax.set_xlabel("dates")
    ax.set_ylabel("wavenumber")
    fig.tight_layout()
    ofile=outdir+"tRATIO."+oar+'.glb'+".png"
    fig.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(fig)
           
    gir, br = plt.subplots()
    linestyle='-'
    br.semilogx(kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color='k', label='Global')
    for ilat, lat in enumerate(LATS):
        linestyle='-'
        if ( ilat >= nclr ): linestyle='--'
        if ( ilat >= 2*nclr ): linestyle='.'
        br.semilogx(kwave[1:], iPSM[ilat][1:]/iPSE[ilat][1:], linestyle=linestyle, color=clr[ilat%nclr], label=str(lat))
    br.legend()
    br = special_xaxis(br)
    br.set_xlabel("wavelength (km)")
    br.set_ylabel("Ratio PSD(Ensemble Mean)/ PSD(Ensemble Members)")
    br.grid(linestyle=':', color='gray', which='both')
    gir.tight_layout()
    ofile=outdir+"PSW_ratio."+oar+'.lat'+".png"
    gir.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gir)

    gir, br = plt.subplots()
    gie, be = plt.subplots()
    gim, bm = plt.subplots()
    linestyle='-'
    br.semilogx(kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color='k', label='Global')
    be.loglog(kwave[1:], PSE[1:], linestyle='-', color='k', label='Global')
    bm.loglog(kwave[1:], PSM[1:], linestyle='-', color='k', label='Global')
    print('global ratio', PSM[1:]/PSE[1:], 'mean', PSM[1:], 'member', PSE[1:])
    for jlat in range(nlatp):
        linestyle='--'
        minLat=LATP[jlat]
        maxLat=LATP[jlat+1]   
        #if ( jlat == 0 ):
        #    label = 'lat < '+str(maxLat)
        #elif ( jlat == nlatp-1 ):
        #    label = 'lat > '+str(minLat)
        #else:
        #    label = str(minLat)+' < lat < '+str(maxLat)
        if ( minLat < 0 ):
            sminLat = str(np.abs(minLat))+udeg+'S'
        elif ( minLat > 0):
            sminLat = str(minLat)+udeg+'N'
        elif ( minLat == 0 ):
            sminLat = str(minLat)+udeg
        else:
            sminLat = str(minLat)+udeg
        if ( maxLat < 0 ):
            smaxLat = str(np.abs(maxLat))+udeg+'S'
        elif ( maxLat > 0):
            smaxLat = str(maxLat)+udeg+'N'
        elif ( maxLat == 0 ):
            smaxLat = str(maxLat)+udeg
        else:
            smaxLat = str(maxLat)+udeg
        label = sminLat+' < lat < '+smaxLat
        
        print('jlat ratio', jlat, label, jPSM[jlat][1:]/jPSE[jlat][1:], 'mean', jPSM[jlat], 'member', jPSE[jlat])
        br.semilogx(kwave[1:], jPSM[jlat][1:]/jPSE[jlat][1:], linestyle=linestyle, color=cl5[jlat%5], label=label)
        be.loglog(kwave[1:], jPSE[jlat][1:], linestyle=linestyle, color=cl5[jlat%5], label=label)
        bm.loglog(kwave[1:], jPSM[jlat][1:], linestyle=linestyle, color=cl5[jlat%5], label=label)
    br.legend()
    br = special_xaxis(br)
    br.set_xlabel("wavelength (km)")
    br.set_ylabel("Ratio PSD(Ensemble Mean) / PSD(Ensemble Members)")
    br.grid(linestyle=':', color='gray', which='both')
    gir.tight_layout()
    ofile=outdir+"PSW_ratio."+oar+'.Lat'+".png"
    gir.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gir)
    be.legend()
    be = special_xaxis(be)
    be.set_xlabel("wavelength (km)")
    be.set_ylabel("PSD "+field_id+units)
    be.grid(linestyle=':', color='gray', which='both')
    gie.tight_layout()
    ofile=outdir+"PSW_loglogE."+oar+'.Lat'+".png"
    gie.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gie)
    bm.legend()
    bm = special_xaxis(bm)
    bm.set_xlabel("wavelength (km)")
    bm.set_ylabel("Ratio PSD(Ensemble Mean) / PSD(Ensemble Members)")
    bm.grid(linestyle=':', color='gray', which='both')
    gim.tight_layout()
    ofile=outdir+"PSW_loglogM."+oar+'.Lat'+".png"
    gim.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gim)

    km3 = np.where( ( (1.0/kwave) > 195 ) & ( (1.0/kwave) < 205 ) )[0][0]
    km4 = np.where( ( (1.0/kwave) > 95 ) & ( (1.0/kwave) < 105 ) )[0][0]
    km3range = range(max([0,km3-2]),min([km3+5, len(kwave)-1]))
    km4range = range(max([0,km4-2]),min([km4+5, len(kwave)-1]))
    Km3 = PSE[km3]*(kwave/kwave[km3])**(-3)
    Km4p5 = PSE[km4]*(kwave/kwave[km4])**(-4.5)
    labkm3='k^(-3)'
    labkm3="k"+supminus+su3
    if usetex: labkm3='$k^{-3}$'
    labkm4p5='k^(-4.5)'
    labkm4p5="k"+supminus+su4+hdot+su5
    if usetex: labkm4p5='$k^{-4.5}$'
    
    gig, bx = plt.subplots()
    gir, br = plt.subplots()
    bx.loglog(kwave[1:], PSM[1:], linestyle='-', color='k', label='Ensemble Mean', linewidth=2.0)
    bx.loglog(kwave[1:], PSE[1:], linestyle='--', color='k', label='Ensemble Member', linewidth=2.0)
    bx.loglog(kwave[km3range], Km3[km3range], linestyle=':', color='r', linewidth=2.0)#, label=labkm3)
    bx.loglog(kwave[km4range], Km4p5[km4range], linestyle=':', color='b', linewidth=2.0)#, label=labkm4p5)
    br.semilogx(kwave[1:], PSM[1:]/PSE[1:], linestyle='-', color='k', label='Ensemble Mean/Ensemble Members')
    bx.legend()
    # label k-3 and k-4.5 lines in place.  May need to offset image from coordinates given.
    km3box = OffsetImage(imgkm3, zoom=0.50)
    km4box = OffsetImage(imgkm4p5, zoom=0.50)
    km3art = AnnotationBbox(km3box, (kwave[km3], PSE[km3]), frameon=False, box_alignment=(0,0))
    km4art = AnnotationBbox(km4box, (kwave[km4], PSE[km4]), frameon=False, box_alignment=(0,0))
    bx.add_artist(km3art)
    bx.add_artist(km4art)
    
    bx = special_xaxis(bx)
    bx.set_xlabel("wavelength (km)")
    bx.set_ylabel("PSD"+field_id+units)
    bx.grid(linestyle=':', color='gray', which='both')
    gig.tight_layout()
    print(outdir, oar)
    ofile=outdir+"PSW_loglog."+oar+'.glb'+".png"
    gig.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gig)
    br.legend()
    br = special_xaxis(br)
    br.set_xlabel("wavelength (km)")
    br.set_ylabel("Ratio PSD(Ensemble Mean) / PSD(Ensemble Members)")
    br.grid(linestyle=':', color='gray', which='both')
    gir.tight_layout()
    ofile=outdir+"PSW_ratio."+oar+'.glb'+".png"
    gir.savefig(ofile, dpi = 300, bbox_inches = "tight")
    plt.close(gir)
    GDX = BOX_DNFO['GDX'] 
    gdx = BOX_DNFO['gdx']

    fig, ax = plt.subplots()
    
    #ZNOTE:  VKMN/VK05 are already wavelengths, not wavenumbers.
    print('VLAT', VLAT)
    print('VKMN', VKMN)
    ax.plot(VLAT, VKMN, linestyle='-', color='r', label='Minimum Ratio')
    #ax.plot(VLAT, VK05, linestyle='--', color='b', label='Ratio = 0.5')
    ax.legend()
    ax.set_xlabel('latitude')
    ax.set_ylabel('length scale km')
    ofile=outdir+"LATS."+oar+".png"
    fig.savefig(ofile, dpi=300, bbox_inches = 'tight')
    plt.close(fig)
        
    izero = np.where(K05 == 0 )
    KFN = K05[:]
    if ( len(izero[0]) > 0 ):
        KFN[izero] = 1.0 / GDX
    LENGTH = 1.0 / KFN
    LENGTH[izero] = 0.0
    print('Max/mean length 05', np.max(LENGTH), np.mean(LENGTH))
    latloc=[-75, -45, -15, 15, 45, 75]
    ctile.cplot_tiles(BOXES, LENGTH, SCALE=[2*gdx, 0.4*GDX], cmap='YlGnBu', project='PlateCarree', outfile=outdir+'BOX05_'+oar+'.png', alpha=1.0, add_gridlines=True, latloc=latloc, lonloc=None)

    izero = np.where(KMN == 0 )
    KFN = KMN[:]
    if ( len(izero[0]) > 0 ):
        KFN[izero] = 1.0 / GDX
    LENGTH = 1.0 / KFN
    LENGTH[izero] = 0.0
    print('Max/mean length MN', np.max(LENGTH), np.mean(LENGTH))
    ctile.cplot_tiles(BOXES, LENGTH, SCALE=[2*gdx, 0.2*GDX], cmap='YlGnBu', project='PlateCarree', outfile=outdir+'BOXMN_'+oar+'.png', alpha=1.0, add_gridlines=True, latloc=latloc)

    #KFN = BRT[:]
    #LENGTH = KFN
    print('Min/Max/mean ratio', np.min(BRT), np.max(BRT), np.mean(BRT))
    ctile.cplot_tiles(BOXES, BRT, SCALE=[0, 0.4], cmap='YlGnBu', project='PlateCarree', outfile=outdir+'BOXRT_'+oar+'.png', alpha=1.0, add_gridlines=True, latloc=latloc)

    print('COMPLETED PLOTING')
    return kwave, psd_mean, psd_memb, K05
        
    
