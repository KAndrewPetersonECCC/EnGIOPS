import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import datetime
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import subprocess
import time
        
import ola_functions
import cplot
import binfld

session = None
def set_global_session():
    global session
    if not session:
        session = requests.Session()
    return
    
file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

site3='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives'
site4='/fs/site4/eccc/mrd/rpnenv/dpe000/maestro_archives'

dates = [20200304, 20200603, 20200902, 20201230]
ens_list = range(21)

def check_date(date, outtype=str, dtlen=8):
    if ( (outtype==str) or (outtype==int) ):
      if ( isinstance(date, datetime.datetime) or isinstance(date, datetime.date) ):
        if ( dtlen == 8 ):  
          datestr=date.strftime("%Y%m%d")
        elif ( dtlen == 10 ): 
          datestr=date.strftime("%Y%m%d%H")
        elif ( dtlen == 12 ): 
          datestr=date.strftime("%Y%m%d%H%M")
        elif ( dtlen == 14 ): 
          datestr=date.strftime("%Y%m%d%H%M%S")
        else:
          datestr=date.strftime("%Y%m%d")
      if ( isinstance(date, int) ):  datestr=str(date)
      if ( isinstance(date, str) ): datestr=date
      if ( len(datestr) < dtlen ):
          datestr=datestr+str(0).zfill(dtlen-len(datestr))
      if ( len(datestr) > dtlen ):
          datestr=datestr[:dtlen]
    if ( outtype ==int ): datestr=int(datestr)
    if ( outtype== datetime.datetime ):
      if ( isinstance(date, int) ): date=str(date)
      if ( isinstance(date, str) and ( len(date) == 8 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d')  
      elif ( isinstance(date, str) and ( len(date) == 10 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H')  
      elif ( isinstance(date, str) and ( len(date) == 12 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M')  
      elif ( isinstance(date, str) and ( len(date) == 14 ) ):
        datestr=datetime.datetime.strptime(date, '%Y%m%d%H%M%S')  
      if ( isinstance(date, datetime.datetime) ): datestr=date
      if ( isinstance(date, datetime.date) ): datestr=datetime.datetime(*date.timetuple()[:4])
    return datestr

file='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

def read_DS_ensemble(expt, date, datadir=site3, enslist=ens_list, night=True):
    date8 = check_date(date, dtlen=8)
    dated = check_date(date, dtlen=10)

    DF_list = []
    for ie in enslist:
       ensstr=str(ie)
       print(datadir, expt, ensstr,date8, dated)
       input_file=datadir+'/'+expt+ensstr+'/SAM2/'+date8+'/DIA/'+dated+'_SAM.ola'    
       DS_SST, DS_SSTN, DS = ola_functions.SST_dataframe(input_file)
       if ( night ): 
           DF_list.append(DS_SSTN)
       else:
           DF_list.append(DS_SST)
    return DF_list        
    
def read_IS_ensemble(expt, date, datadir=site3, enslist=ens_list, satellite='ALL'):
    date8 = check_date(date, dtlen=8)
    dated = check_date(date, dtlen=10)
    isat = 0
    if ( isinstance(satellite, int) ): 
        isat=satellite
        satellite=str(satellite)
    elif ( isinstance(satellite, type(None)) ):
        satellite='NONE'
    SAT = satellite.upper()

    DF_list = []
    for ie in enslist:
       ensstr=str(ie)
       print(datadir, expt, ensstr,date8, dated)
       input_file=datadir+'/'+expt+ensstr+'/SAM2/'+date8+'/DIA/'+dated+'_SAM.ola'    
       df_IS_AL, df_IS_C2, df_IS_J2, df_IS_J3, df_IS_J2N, df_IS_H2, df_IS_S3A, df_IS = ola_functions.SSH_dataframe(input_file)
       if ( ( SAT == 'ALL' ) or ( SAT == 'NONE' ) ): 
           DF_list.append(df_IS)
       elif ( ( SAT == 'ALTIKA' ) or ( SAT == 'AL' ) or ( isat == 13 ) ):
           DF_list.append(df_IS_AL)
       elif ( ( SAT == 'CRYOSAT2' ) or ( SAT == 'C2' ) or ( isat == 11 ) ):
           DF_list.append(df_IS_C2)
       elif ( ( SAT == 'JASON2' ) or ( SAT == 'J2' ) or ( isat == 3 ) ):
           DF_list.append(df_IS_J2)
       elif ( ( SAT == 'JASON3' ) or ( SAT == 'J3' ) or ( isat == 15 ) ):
           DF_list.append(df_IS_J3)
       elif ( ( SAT == 'JASON2N' ) or ( SAT == 'J2N' ) or ( isat == 16 ) ):
           DF_list.append(df_IS_AL)
       elif ( ( SAT == 'HY2A' ) or ( SAT == 'H2' ) or ( isat == 14 ) ):
           DF_list.append(df_IS_H2)
       elif ( ( SAT == 'SENTINEL3A' ) or ( SAT == 'SENTINEL') or ( SAT == 'S3A' ) or ( isat == 17 ) ):
           DF_list.append(df_IS_S3A)
       else:
           DF_list.append(df_IS)
    return DF_list           

def rank(list):
    posn = [ ( value > 0 ) for value in list ]
    rank_val = sum(posn)
    return rank_val
    
def rank_DS_obs(DF_list):
    nobs = len(DF_list[0])
    rank_np = np.zeros(nobs)
    hist_np = np.zeros(len(DF_list)+1)
    for iobs in range(nobs):
        list = [ DF['misfit'].values[iobs] for DF in DF_list ]
        rank_vl = rank(list)
        rank_np[iobs] = rank_vl
        hist_np[rank_vl] = hist_np[rank_vl]+1
    return rank_np, hist_np

def create_dates(date_start, date_final, date_inter):
    dates=[]
    date_start = check_date(date_start, outtype=datetime.datetime)
    date_final = check_date(date_final, outtype=datetime.datetime)
    
    date = date_start
    while ( date <= date_final ):
        dates.append(date)
        date = date + datetime.timedelta(days=date_inter)
    return dates
    
def rank_over_range(expt, dates, obstype='DS', enslist=ens_list, datadir=site3):
    nens=len(enslist)
    hist_sm = np.zeros(nens+1)
    for date in dates:
        # Not sure if this will be generalizable yet -- but leave option open.
        if ( obstype == 'DS' ):
            DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir)
            rank_np, hist_np = rank_DS_obs(DF_list)
        hist_sm = hist_sm + hist_np
    return hist_sm

def plot_histogram(hist_np, title, pfile):
    if ( isinstance(hist_np, list) ): hist_np = np.array(hist_np).astype(float)
    fig=plt.figure()
    axe=plt.subplot()
    norm_np = hist_np.astype(float) / float(sum(hist_np))
    xaxis = np.arange(len(hist_np)).astype(float)
    xaxis = xaxis - 0.5
    axe.bar(range(len(hist_np)), norm_np, width=1)
    axe.set_title(title)
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)
    return
    
def plot_histograms(hist_np_list, labels, title, pfile):
    fig=plt.figure()
    axe=plt.subplot()
    nh = len(hist_np_list)
    width=1.0 / nh
    xaxis = np.arange(len(hist_np_list[0])).astype(float)
    xaxis = xaxis - 0.5
    xaxis = xaxis + 0.5*width
    for ih, hist_np in enumerate(hist_np_list):
        if ( isinstance(hist_np, list) ): hist_np = np.array(hist_np).astype(float)
        norm_np = hist_np.astype(float) / float(sum(hist_np))
        axe.bar(xaxis, norm_np, width=1, label=labels[ih])
        xaxis = xaxis + width
    axe.set_title(title)
    axe.legend()
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)
    return
    
def plot_rank_over_range(odir, expt, date_range, obstype='DS', enn=21, datadir=site3):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    title='Rank Histogram over Period '+datestr0+'-'+datestr1
    pfile=odir+'/'+expt+'_'+datestrc+'.rhist'
    
    hist_sm = rank_over_range(expt, dates, obstype='DS', enslist=enslist, datadir=datadir)
    plot_histogram(hist_sm, title, pfile)
    return
    
def plot_ranks_over_range(oprefix, expts, date_range, labels=None, obstype='DS', enn=21, datadir=site3):
    print(expts)
    print(labels)
    print(None)
    print( isinstance(labels, type(None)))
    if ( isinstance(labels, type(None)) ): labels=expts
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    title='Rank Histogram over Period '+datestr0+'-'+datestr1
    pfile=oprefix+'_'+datestrc+'.rhist'
    hist_sm_list = []
    for expt in expts:    
        hist_sm = rank_over_range(expt, dates, obstype='DS', enslist=enslist, datadir=datadir)
        hist_sm_list.append(hist_sm)
    plot_histogram(hist_sm_list, title, pfile)
    return

def ensemble_mean_misfit(DF_list):
    misfit_list = [ DF['misfit'].values for DF in DF_list]
    misfit_mean = sum(misfit_list) / len(misfit_list)
    DF_mean = DF_list[0].copy()
    DF_mean['misfit'] = misfit_mean
    return DF_mean

def ensemble_vari_misfit(DF_list):
    misfit_list = [ DF['misfit'].values for DF in DF_list]
    misfit_mean = sum(misfit_list) / len(misfit_list)
    misfit_anom = [ ( misfit - misfit_mean ) for misfit in misfit_list]
    misfit_squa = [ misfit**2 for misfit in misfit_anom]
    misfit_vari = sum(misfit_squa) / len(misfit_squa) 
    DF_mean = DF_list[0].copy()
    DF_mean['misfit'] = misfit_mean
    DF_mean['errvar'] = misfit_vari
    return DF_mean

def bin_errors_over_range(expt, dates, obstype='DS', enslist=ens_list, datadir=site3, **kwargs):
    night=True
    satellite='ALL'
    for key, value in kwargs.items():
        print(key, value)
        if ( key == 'night' ):
            night=value
        if ( key == 'satellite' ):
            satellite=value
        
    
    grid_lon, grid_lat, lon_bin, lat_bin, grid_sum, grid_cnt = binfld.make_bin_grid(ddeg=1)
    for date in dates:
        if ( obstype == 'DS' ):
            DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir, night=night)
        elif ( obstype == 'IS' ):
            DF_list = read_IS_ensemble(expt, date, enslist=enslist, datadir=datadir, satellite=satellite)
        DF_mean = ensemble_vari_misfit(DF_list)
        lon = DF_mean['Lon'].values
        lat = DF_mean['Lat'].values
        misfit = DF_mean['misfit'].values
        squerr = misfit**2
        errvar = DF_mean['errvar'].values
        bin_misfit , cnt_misfit = binfld.binfldsumcum(lon, lat, misfit, lon_bin, lat_bin, bin_misfit, cnt_misfit)
        bin_squerr , cnt_squerr = binfld.binfldsumcum(lon, lat, squerr, lon_bin, lat_bin, bin_squerr, cnt_squerr)
        bin_errvar , cnt_errvar = binfld.binfldsumcum(lon, lat, errvar, lon_bin, lat_bin, bin_errvar, cnt_errvar)
    tot_cnt_misfit = np.sum(cnt_misfit)
    tot_cnt_squerr = np.sum(cnt_squerr)
    tot_cnt_errvar = np.sum(cnt_errvar)
    if ( tot_cnt_squerr != tot_cnt_misfit ): print('Warning, squerr/misfit cnt error', tot_cnt_misfit, tot_cnt_squerr)
    if ( tot_cnt_errvar != tot_cnt_misfit ): print('Warning, errvar/misfit cnt error', tot_cnt_misfit, tot_cnt_errvar)
    avg_misfit = binfld.binfldsumFIN(bin_misfit, cnt_misfit)
    avg_squerr = binfld.binfldsumFIN(bin_squerr, cnt_squerr)
    avg_errvar = binfld.binfldsumFIN(bin_errvar, cnt_errvar)
  
    return avg_misfit, avg_squerr, avg_errvar, [grid_lon, grid_lat]

def bin_errors_date(expt, date, obstype='DS', enslist=ens_list, datadir=site3, **kwargs):
    night=True
    satellite='ALL'
    for key, value in kwargs.items():
        print(key, value)
        if ( key == 'night' ):
            night=value
        if ( key == 'satellite' ):
            satellite=value
        
    grid_lon, grid_lat, lon_bin, lat_bin, grid_sum, grid_cnt = binfld.make_bin_grid(ddeg=0.5)
    bin_misfit_cum, cnt_misfit_cum = grid_sum.copy(), grid_cnt.copy()
    bin_squerr_cum, cnt_squerr_cum = grid_sum.copy(), grid_cnt.copy()

    if ( obstype == 'DS' ):
        DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir, night=night)
    elif (obstype == 'IS' ):
        DF_list = read_IS_ensemble(expt, date, enslist=enslist, datadir=datadir, satellite=satellite)
	
    bin_misfit_list = []
    bin_sqrerr_list = []
    cnt_misfit_list = []
    cnt_sqrerr_list = []
    for DF in DF_list:
        misfit = DF['misfit'].values
	sqrerr = np.square(misfit)
        bin_misfit, cnt_misfit = binfld.binfldsum(lon, lat, misfit, lon_bin, lat_bin)
	bin_sqrerr, cnt_sqrerr = binfld.binfldsum(lon, lat, misfit, lon_bin, lat_bin)
	bin_misfit_cum = bin_misfit_cum + bin_misfit
	bin_sqrerr_cum = bin_sqrerr_cum + bin_sqrerr
	cnt_misfit_cum = cnt_misfit_cum + cnt_misfit
	cnt_sqrerr_cum = cnt_sqrerr_cum + cnt_sqrerr
	bin_misfit = binfld.binfldsumFIN(bin_misfit, cnt_misfit)
	bin_sqrerr = binfld.binfldsumFIN(bin_sqrerr, cnt_sqrerr)
	bin_misfit_list.append( bin_misfit )
	bin_sqrerr_list.append( bin_sqrerr )
	cnt_misfit_list.append( cnt_misfit )
	cnt_sqrerr_list.append( cnt_sqrerr )
	
   ensemble_mean_bin_misfit = sum(bin_misfit_list) / len(bin_misfit_list)
   ensemble_mean_bin_sqrerr = sum(bin_sqrerr_list) / len(bin_sqrerr_list)

   mean_ensemble_misfit = binfld.binfldsumFIN(bin_misfit_cum, cnt_misfit_cum)
   mean_ensemble_sqrerr = binfld.binfldsumFIN(bin_sqrerr_cum, cnt_sqrerr_cum)
  
   return [grid_lon, grid_lat]

CLEVA=np.arange(-0.9, 1.1, 0.2)
CLEVF=np.arange(0, 1.1, 0.1)
cmap_full='gist_stern_r'
cmap_anom='RdYlBu_r'
def plot_binned_errors(LatLon, fields, titles, pfiles, anomis, clev_full=CLEVF, clev_anom=CLEVA):
   grid_lon, grid_lat = LatLon
   for ii in range(len(fields)):
       field=fields[ii]
       title=titles[ii]
       pfile=pfiles[ii]
       anomi=anomis[ii]
       if ( anomi == 0 ): 
           cmap=cmap_full
           levels=clev_full
       if ( anomi == 1 ): 
           cmap=cmap_anom
           levels=clev_anom
       cplot.pcolormesh(grid_lon, grid_lat, field, outfile=pfile, levels=levels, cmap=cmap, obar='horizontal')
   return
   
def plot_errors_over_range(odir, expt, date_range, obstype='DS', enn=21, clev_full=CLEVF, clev_anom=CLEVA, datadir=site3):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    title1='Mean Error '+datestr0+'-'+datestr1
    title2='RMSE Ensemble Mean '+datestr0+'-'+datestr1
    title3='STD. Dev. Ensemble '+datestr0+'-'+datestr1
    title4='Std. Dev. Error wrt Time '+datestr0+'-'+datestr1
    pfile1=odir+'/'+expt+'_'+datestrc+'.mean.png'
    pfile2=odir+'/'+expt+'_'+datestrc+'.rmse.png'
    pfile3=odir+'/'+expt+'_'+datestrc+'.vari.png'
    pfile4=odir+'/'+expt+'_'+datestrc+'.verr.png'
    
    titles=[title1, title2, title3, title4]
    pfiles=[pfile1, pfile2, pfile3, pfile4]

    avg_misfit, avg_squerr, avg_errvar, [grid_lon, grid_lat] = bin_errors_over_range(expt, dates, obstype='DS', enslist=enslist, datadir=datadir)
    avg_varerr = avg_squerr - np.square(avg_misfit)
    fields=[avg_misfit, np.sqrt(avg_squerr), np.sqrt(avg_errvar), np.sqrt(avg_varerr)]
    plot_binned_errors([grid_lon, grid_lat], fields, titles, pfiles, [1, 0, 0, 0], clev_full=CLEVF, clev_anom=CLEVA)
    xfields=[avg_misfit, np.sqrt(avg_squerr), np.sqrt(avg_varerr)]
    yfields=[np.sqrt(avg_errvar), np.sqrt(avg_errvar), np.sqrt(avg_errvar)]
    titles = ['Spread vs. Error', 'Spread vs. Error', 'Spread vs. Error']
    ofile1 = odir+'/'+expt+'_'+datestrc+'.mean.scat.png'
    ofile2 = odir+'/'+expt+'_'+datestrc+'.rmse.scat.png'
    ofile3 = odir+'/'+expt+'_'+datestrc+'.verr.scat.png'
    ofiles = [ofile1, ofile2, ofile3]
    xlabels=['mean error', 'rmse error', 'std. error']
    ylabels=['ens. std. dev.', 'ens. std. dev.', 'ens. std. dev.']
    plot_scatter_onbin(xfields, yfields, titles, ofiles, xlabels, ylabels, [1, 0, 0, 0], [0, 0, 0, 0], grid_lat)
    
    return

def plot_scatter_onbin(xfield, yfield, title, ofile, xlabel, ylabel, xanom, yanom, lat, obs_err=0.3):
    xmax=2
    ymax=2
    amax=max([xmax, ymax])
    
    if ( isinstance(xfield, list) ):
        for ifield, xfieldi in enumerate(xfield):
            plot_scatter_onbin(xfield[ifield], yfield[ifield], title[ifield], ofile[ifield], xlabel[ifield], ylabel[ifield], xanom[ifield], yanom[ifield], lat)
        return
    ivalid = np.where(xfield.mask == False )
    alat = np.absolute(lat[ivalid])
    colors=[]
    for ii in range(len(alat)):
        if   ( alat[ii] < 15 ): colors.append('m')
        elif ( alat[ii] < 30 ): colors.append('r')
        elif ( alat[ii] < 45 ): colors.append('y')
        elif ( alat[ii] < 60 ): colors.append('g')
        elif ( alat[ii] < 75 ): colors.append('c')
        elif ( alat[ii] < 90 ): colors.append('b')
    fig, axe = plt.subplots()
    axe.scatter(xfield[ivalid], yfield[ivalid], color=colors,s=0.1)  
    axe.plot([0,     amax], [0, amax], color='k')
    if ( xanom == 1 ): 
        axe.plot([0,-1.0*amax], [0, amax], color='k')
        axe.set_xlim([-1.0*xmax, xmax])
    else:
        axe.set_xlim([0, xmax])
    if ( yanom == 1 ): 
        axe.set_ylim([-1.0*ymax, ymax])
        axe.plot([0, amax], [0, -1.0*amax], color='k')
        if ( xanom == 1 ):
            axe.plot([0,-1.0*amax], [0, -1.0*amax], color='k')
    else:
        axe.set_ylim([0, ymax])
    axe.set_xlabel(xlabel)
    axe.set_ylabel(ylabel)
    circle = plt.Circle((0.0, 0.0), obs_err, color='k', fill=False)
    axe.add_patch(circle)
    fig.savefig(pfile+'.png')
    plt.close(fig)
    return pfile+'.png'

def plot_scatter(odir, expt, date, axis_range=[2, 2], obs_err=0.3, enslist=ens_list, datadir=site3):
    xmax=axis_range[0]
    ymax=axis_range[1]
    amax=np.max([xmax, ymax])
    date=check_date(date, outtype=datetime.datetime)
    datestr=check_date(date, outtype=str)
    pfile=odir+'/'+expt+'_'+datestr+'.scat'
    DF_list = read_DS_ensemble(expt, date, enslist=enslist, datadir=datadir)
    DF_mean =  ensemble_vari_misfit(DF_list)
    
    misfit = DF_mean['misfit'].values
    errstd = np.sqrt(DF_mean['errvar'].values)  
    
    lat = DF_mean['Lat'].values
    alat = np.absolute(lat)
    nobs=len(misfit)
    colors=[]
    for ii in range(nobs):
        if   ( alat[ii] < 15 ): colors.append('m')
        elif ( alat[ii] < 30 ): colors.append('r')
        elif ( alat[ii] < 45 ): colors.append('y')
        elif ( alat[ii] < 60 ): colors.append('g')
        elif ( alat[ii] < 75 ): colors.append('c')
        elif ( alat[ii] < 90 ): colors.append('b')
    fig, axe = plt.subplots()
    axe.scatter(misfit, errstd, color=colors,s=0.1)
    axe.plot([0,     amax], [0, amax], color='k')
    axe.plot([0,-1.0*amax], [0, amax], color='k')
    axe.set_xlim([-1.0*xmax, xmax])
    axe.set_ylim([0, ymax])
    axe.set_xlabel('mean error')
    axe.set_ylabel('std. dev.')
    circle = plt.Circle((0.0, 0.0), obs_err, color='k', fill=False)
    axe.add_patch(circle)
    fig.savefig(pfile+'.png')
    plt.close(fig)
    return pfile+'.png'

def plot_scatter_in_range(odir, expt, date_range, axis_range=[2, 2], obs_err=0.3, enn=21, datadir=site3):
    enslist=range(enn)
    dateinc=7
    if ( len(date_range) > 2 ): dateinc=date_range[3]
    dates=create_dates(date_range[0], date_range[1], dateinc)
    datestr0=check_date(date_range[0])
    datestr1=check_date(date_range[1])
    datestrc=datestr0+'_'+datestr1
    pfilef=odir+'/'+expt+'_'+datestrc+'.scat.gif'


    pfiles=[]    
    for date in dates:
        pfile=plot_scatter(odir, expt, date, axis_range=axis_range, obs_err=obs_err, enslist=enslist, datadir=datadir)
        pfiles.append(pfile)

    command=[['convert', '-d', '50']+pfiles+['pfilef']]
    print(command)
    subprocess.call(command)
    return
