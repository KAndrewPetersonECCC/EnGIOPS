from importlib import reload
import sys
this_dir='/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python'
sys.path.insert(0, this_dir)

import matplotlib.pyplot as plt
import datetime
import numpy as np
import scipy.stats


import fft_giops
import read_dia
import check_date
import rank_histogram
import read_grid
import isoheatcontent

hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

def cycle_lon(lons):
    clons = (lons+180)%360 - 180
    return clons

def read_test_fld(var='T'):
    testdate=check_date.check_date(20220601, outtype=datetime.datetime)
    lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', testdate, fld=var, file_pre='ORCA025-CMC-ANAL_1d_')
    MTFLD = sum(ETFLD)/len(ETFLD)
    return lone, late, ETFLD, MTFLD

def test1():  
    lonee, late, ETFLD, MTFLD = read_test_fld()

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
    wavenumber = 2*np.pi * np.fft.fftfreq(N, gdx)  # actually sampling frequency (so mult by 2pi for k)
    L = int((N-1)/2)

    plt.loglog(2*np.pi/wavenumber[1:L+1], FLD_PSD[1:L+1], color='b')
    plt.loglog(2*np.pi/wavenumber[1:L+1], MFLD_PSD[1:L+1], color='r')
    plt.savefig('psd.png')
    plt.close()

    plt.loglog(2*np.pi/wavenumber[1:L+1], FLD_PSD[1:L+1]/MFLD_PSD[1:L+1], color='k')
    plt.savefig('rpsd.png')
    plt.close()
    return

def create_BOXES(gdx=25.0, GDX=2000.0, threshold=0.95):
    CEARTH=40000
    #GDX=2500.0 #km
    #gdx = 25.0 #km

    mask = read_grid.read_mask(var='tmask')
    sask = np.squeeze(mask)[0,:,:]

    lone, late, ETFLD, MTFLD = read_test_fld()
    TSURF=MTFLD[0,0,:,:]

    BOXES=[]
    GRIDS=[]
    NBOX =  np.floor(CEARTH / 2 / GDX).astype(int)
    LATS = np.arange(NBOX) * (180.0/NBOX) - 90
    LATS = LATS[1:-1]
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

def test_cycle(dates=rank_histogram.create_dates(20210609, 20220601,7), var='SST'):
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    GDX=2500.0 #km 
    gdx = 25.0 #km
    LLGRID, BOX = fft_giops.create_box( (-172,0), size=GDX, dx=gdx, theta=0.0 )
    Nx, Ny = LLGRID[0].shape
    if ( Nx == Ny ): N=Nx

    knorm = fft_giops.find_wavenumber_norm(N, gdx)
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
    if ( len(dates) > 5 ):
        lst = list(range(4))
    elif ( len(dates) > 8 ):
        lst = [0, 4, 6, 8]
    elif ( len(dates) > 13 ):
        lst = [0, 4, 8, 13]
    elif ( len(dates) > 26 ):
         lst = [0, 4, 13, 26]
    for idate, date in enumerate(dates):
        print(date)
        if ( var == 'D20' ):
            lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
        else:
            lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', date, fld=var, file_pre='ORCA025-CMC-ANAL_1d_')
        ESST = [ np.squeeze(eTFLD/1) for eTFLD in ETFLD]
        if ( var == 'T' ):
            level=22
            ESST = [ np.squeeze(eSST[level,:,:]/1) for eSST in ESST]
            deptht=read_dia.read_sam2_levels()
            print('Subsetting to ', deptht[level])
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
        MSST = sum(ESST)/ne
        if ( idate == 0 ):
           fft_giops.pcolormesh_with_box(lone, late, MSST, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=[BOX], outfile='Box.'+oar+'.png')
        SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, (lone, late), LLGRID, method='nearest')
        PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
        Mbins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
        Mbins = Mbins+Mbins_add
        for eSST in ESST:
            SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, (lone, late), LLGRID, method='nearest')
            PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
            Ebins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
            Ebins = Ebins+Ebins_add/ne
        if ( idate in lst ):
            print(idate, lst.index(idate))
            ax.loglog(2*np.pi/kvals, Mbins/(idate+1), linestyle='-', color=clr[lst.index(idate)], label=str(idate))
            ax.loglog(2*np.pi/kvals, Ebins/(idate+1), linestyle='--', color=clr[lst.index(idate)], label=str(idate))
            ar.semilogx(2*np.pi/kvals, Mbins/Ebins, linestyle='-', color=clr[lst.index(idate)], label=str(idate))
    ax.loglog(2*np.pi/kvals, Mbins/nt, linestyle='-', color='k', label=str(nt))
    ax.loglog(2*np.pi/kvals, Ebins/nt, linestyle='--', color='k', label=str(nt))
    ar.semilogx(2*np.pi/kvals, Mbins/Ebins, linestyle='-', color='k', label=str(nt))
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
def box_cycle(date=datetime.datetime(2021,6,2), var='SST', BOX_INFO=create_BOXES(gdx=25.0, GDX=1500, threshold=0.95)):
    BOXES, GRIDS, LATS = BOX_INFO 
    oar=var
    if ( var == 'T' ): oar='T100'
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    GDX=1500.0 #km 
    gdx = 25.0 #km
    #LLGRID, BOX = fft_giops.create_box( (-172,0), size=GDX, dx=gdx, theta=0.0 )
    nbox = len(BOXES)
    print('NUMBER OF BOXES', nbox)

    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx

    knorm = fft_giops.find_wavenumber_norm(N, gdx)
    kbins, kvals = fft_giops.setup_Kbins(N, gdx)

    Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    Ebins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    fig, ax = plt.subplots()
    fir, ar = plt.subplots()
    lats = [-70, -55, -35]
    clr = ['r', 'c', 'g', 'b', 'm']
    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    ncol=len(clr)

    if ( var == 'D20' ):
        lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
    else:
        lone, late, ETFLD = read_dia.read_ensemble(mir5, 'GIOPS_T', date, fld=var, file_pre='ORCA025-CMC-ANAL_1d_')
    ESST = [ np.squeeze(eTFLD/1) for eTFLD in ETFLD]
    if ( var == 'T' ):
        level=22
        ESST = [ np.squeeze(eSST[level,:,:]/1) for eSST in ESST]
        deptht=read_dia.read_sam2_levels()
        print('Subsetting to ', deptht[level])
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
    MSST = sum(ESST)/ne
    fft_giops.pcolormesh_with_box(lone, late, MSST, levels=None, ticks=None, project='PlateCarree',box=[-180, 180, -90, 90], obar='horizontal', plot_boxes=BOXES, outfile='BOX/'+oar+'.png')
    Mbins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    Ebins, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    fig, ax = plt.subplots()
    fir, ar = plt.subplots()
    lcol = -1
    Mbins_list = []
    Ebins_list = []
    for ibox, BOX in enumerate(BOXES):
        print(ibox, nbox, BOX)
        lat = BOX[0][1]
        icol = 0
        for ii, LAT in enumerate(LATS):
            if ( lat > LAT-1 ): icol=ii
        big, bax = plt.subplots()
        bir, bar = plt.subplots()
        LLGRID = GRIDS[ibox]
        SST_BOX = fft_giops.interpolate_to_box_with_mask(MSST, (lone, late), LLGRID, method='nearest')
        PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
        Mbins_add, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
        Mbins = Mbins+Mbins_add/nbox
        Ebins_add, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
        for eSST in ESST:
            SST_BOX = fft_giops.interpolate_to_box_with_mask(eSST, (lone, late), LLGRID, method='nearest')
            PSD, FFT = fft_giops.get_fft_ps(SST_BOX)
            Ebins_edd, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD.flatten(), statistic = "mean", bins = kbins)
            Ebins_add = Ebins_add+Ebins_edd/ne
        Ebins = Ebins+Ebins_add/nbox
        if ( lcol < icol ): 
            lcol=icol
            ax.loglog(2*np.pi/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
            ar.semilogx(2*np.pi/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol], label=str(LATS[lcol]))
        else:
            ax.loglog(2*np.pi/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol])
            ar.semilogx(2*np.pi/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol])
        ax.loglog(2*np.pi/kvals, Ebins_add, linestyle='--', color=clr[icol%ncol])
        bax.loglog(2*np.pi/kvals, Mbins_add, linestyle='-', color=clr[icol%ncol], label='Ensemble Mean')
        bax.loglog(2*np.pi/kvals, Ebins_add, linestyle='--', color=clr[icol%ncol], label='Mean Ensemble')
        bar.semilogx(2*np.pi/kvals, Mbins_add/Ebins_add, linestyle='-', color=clr[icol%ncol], label=str(ibox))
        bax.legend()
        crstr = '('+str(BOX[0][0])+'E, '+ str(BOX[0][1])+'N)'
        bax.set_title('PSD Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        bax.set_xlabel("$lambda$")
        bax.set_ylabel("$P(k)$")
        big.tight_layout()
        big.savefig("BOX/GPSD_loglog."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        plt.close(big)
        bar.set_title('Ratio Box '+str(ibox).zfill(3)+' Corner:'+crstr)
        bar.set_xlabel("$lambda$")
        bar.set_ylabel("Ratio")
        bir.tight_layout()
        bir.savefig("BOX/GPSD_ratio."+oar+"."+str(ibox).zfill(3)+".png", dpi = 300, bbox_inches = "tight")
        plt.close(bir)
        Mbins_list.append(Mbins_add)
        Ebins_list.append(Ebins_add)
    ax.loglog(2*np.pi/kvals, Mbins, linestyle='-', color='k', label='Global Mean')
    ax.loglog(2*np.pi/kvals, Ebins, linestyle='--', color='k')
    ar.semilogx(2*np.pi/kvals, Mbins/Ebins, linestyle='-', color='k', label='Global Mean')
    ax.legend()
    ax.set_xlabel("$lambda$")
    ax.set_ylabel("$P(k)$")
    fig.tight_layout()
    fig.savefig("BOX/GPSD_loglog."+oar+".png", dpi = 300, bbox_inches = "tight")
    plt.close(fig)
    ar.legend()
    ar.set_xlabel("$lambda$")
    ar.set_ylabel("Ratio")
    fir.tight_layout()
    fir.savefig("BOX/GPSD_ratio."+oar+".png", dpi = 300, bbox_inches = "tight")
    plt.close(fir)
    
    return kvals, Mbins, Ebins, Mbins_list, Ebins_list   

def cycle_dates_global(var, dates=rank_histogram.create_dates(20210609, 20220601,7)):
    ndates=len(dates)
    BOX_INFO=create_BOXES(gdx=gdx, GDX=GDX, threshold=0.95)
    BOXES, GRIDS, LATS = BOX_INFO 
    nbox = len(BOXES)
    Nx, Ny = GRIDS[0][0].shape
    if ( Nx == Ny ): N=Nx
    knorm = fft_giops.find_wavenumber_norm(N, gdx)
    kbins, kvals = fft_giops.setup_Kbins(N, gdx)

    clr = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

    Mbins_sum, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    Ebins_sum, __, __ = scipy.stats.binned_statistic(knorm.flatten(), np.zeros(knorm.shape).flatten(), statistic = "mean",bins = kbins)
    dat_fig, dat_ax = plt.subplots()
    dat_fir, dat_ar = plt.subplots()
    Mbins_sum_list = []
    Ebins_sum_list = []
    lst_fig = []
    lst_fig = []
    for ibox in range(nbox):
        Mbins_sum_list.append(Mbins_sum.copy())
        Ebins_sum_list.append(Ebins_sum.copy())
        tmp_fig, tmp_ax = plt.subplots()
        lst_fig.append((tmp_fig, tmp_ax))
        tmp_fir, tmp_ar = plt.subplots()
        lst_fig.append((tmp_fir, tmp_ax))
    for date in dates:
        kvals, Mbins, Ebins, Mbins_list, Ebins_list = box_cycle(date=date, var=var, BOX_INFO=BOX_INFO)
        Mbins_sum = Mbins_sum + Mbins
        Ebins_sum = Ebins_sum + Ebins
        for ibox in range(nbox):
            Mbins_sum_list[ibox] = Mbins_sum_list[ibox] + Mbins_list[ibox]
            Ebins_sum_list[ibox] = Ebins_sum_list[ibox] + Ebins_list[ibox]
    Mbins_sum = Mbins_sum / ndates
    Ebins_sum = Ebins_sum / ndates
    for ibox in range(nbox):
        Mbins_sum_list[ibox] = Mbins_sum_list[ibox] / ndates
        Ebins_sum_list[ibox] = Ebins_sum_list[ibox] / ndates
    
    
    
