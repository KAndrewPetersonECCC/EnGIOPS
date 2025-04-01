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

dates=rank_histogram.create_dates(20210609, 20220601, 7)
fourier_analysis.cycle_dates_done(dates, var='K15', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='KE0', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='TAUK', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='Tsppt', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='MLD', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='SST', indir='BOX/', outdir='BOX/')
fourier_analysis.cycle_dates_done(dates, var='T', indir='BOX/', outdir='BOX/')


EOP
