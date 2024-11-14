#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/fourier_second.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/fourier_second.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOP
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import datetime
import check_date

import fourier_analysis
import rank_histogram

#files=glob.glob('BOX/'+sar+'_psd_????????.nc')
#dates = sorted([ file[-11:-3] for file in files])

dates=rank_histogram.create_dates(20210609, 20220601, 7)
try:
    fourier_analysis.cycle_dates_done(dates, var='K15', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'K15')
    fourier_analysis.cycle_dates_done(None, var='K15', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='KE0', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'KE0')
    fourier_analysis.cycle_dates_done(None, var='KE0', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='TAUK', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'TAUK' )
    fourier_analysis.cycle_dates_done(None, var='TAUK', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='Tsppt', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'Tsppt')
    fourier_analysis.cycle_dates_done(None, var='Tsppt', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='MLD', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'MLD')
    fourier_analysis.cycle_dates_done(None, var='MLD', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='SST', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'SST')
    fourier_analysis.cycle_dates_done(None, var='SST', indir='BOX/', outdir='BOX/')

try:
    fourier_analysis.cycle_dates_done(dates, var='T', indir='BOX/', outdir='BOX/')
except:
    print("RETRYING WITH NONE",'SST')
    fourier_analysis.cycle_dates_done(None, var='T', indir='BOX/', outdir='BOX/')

skip = True
if ( not skip ):
  try:
    fourier_analysis.cycle_dates_done(dates, var='K15', indir='BOX.1/', outdir='BOX.1/')
  except:
    print("RETRYING WITH NONE", "K15")
    fourier_analysis.cycle_dates_done(None, var='K15', indir='BOX.1/', outdir='BOX.1/')

  try:
    fourier_analysis.cycle_dates_done(dates, var='KE0', indir='BOX.1/', outdir='BOX.1/')
  except:
    print("RETRYING WITH NONE", 'KE0',)
    fourier_analysis.cycle_dates_done(None, var='KE0', indir='BOX.1/', outdir='BOX.1/')



EOP
