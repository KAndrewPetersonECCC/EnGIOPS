#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_long.sh -cpus 20 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

#from multiprocessing import set_start_method
#set_start_method("spawn")
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram
import ensemble_functions

ANN_dates = rank_histogram.create_dates(20210602, 20220601, 7)
JUN_dates = rank_histogram.create_dates(20210602, 20210630, 7)
JUL_dates = rank_histogram.create_dates(20210707, 20210728, 7)
AUG_dates = rank_histogram.create_dates(20210804, 20210825, 7)
SEP_dates = rank_histogram.create_dates(20210901, 20210929, 7)
OCT_dates = rank_histogram.create_dates(20211006, 20211027, 7)
NOV_dates = rank_histogram.create_dates(20211103, 20211124, 7)
DEC_dates = rank_histogram.create_dates(20211201, 20211229, 7)
JAN_dates = rank_histogram.create_dates(20220105, 20220126, 7)
FEB_dates = rank_histogram.create_dates(20220202, 20220223, 7)
MAR_dates = rank_histogram.create_dates(20220302, 20220330, 7)
APR_dates = rank_histogram.create_dates(20220406, 20220427, 7)
MAY_dates = rank_histogram.create_dates(20220504, 20220601, 7)

ALL_dates = (JUN_dates, JUL_dates, AUG_dates, SEP_dates, OCT_dates, NOV_dates, DEC_dates, JAN_dates, FEB_dates, MAR_dates, APR_dates, MAY_dates, ANN_dates)

expts=('GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T')
labels=('Ensemble', 'Operation', 'Control')
outdir=('ENSEMBLE', 'OPERATION', 'CONTROL')
enss=(21, 0, 1)

read_DF_VP.produce_stats_plot( ANN_dates, expts, enss, labels=labels, outdir=outdir)
print("FINISHED ANN DATES")

for idate, dates in enumerate(ALL_dates[:-1]):
    read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir, mp_expt=True, mp_read=False)
    if ( idate < 12 ):
        print("FINISHED MONTH DATES ", idate)
    else:
        print("FINISHED ANNUAL DATES ", idate)

EOD
