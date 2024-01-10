#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/work2_SSH_OLA.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD
from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import time
import read_DF_VP
import rank_histogram
import read_DF_IS

print("CALCULATE ERRORS")
time0=time.time()
gl_series, rgs_series, bin_series = read_DF_IS.calc_errors_date(20220601, 'GIOPS_T', ens=list(range(21)), deterministic=False, ddir=read_DF_VP.get_mdir(5), mp_read=True)
print("DONE CALCULATE ERRORS", time.time()-time0)

print("PROCESS EXPERIMENT", flush=True)
dates = rank_histogram.create_dates(20210602, 20220728, 7)
expt, gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series = read_DF_IS.process_expt(dates, 'GIOPS_T', list(range(21)), read_DF_VP.get_mdir(5), mp_read=False, mp_date=True, SAT='ALL')
print("FINISH PROCESS EXPERIMENT", flush=True)

expts=('GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T')
print("PROCESS EXPTS", expts, flush=True)
dates = rank_histogram.create_dates(20210602, 20220728, 7)

labels=('Ensemble', 'Operation', 'Control')
enss=(21, 0, 1)
ddir=[read_DF_VP.get_mdir(5,user='dpe000')]*3
outdir=[expt for expt in expts]
outdir=['GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T0']

print("PROCESS EXPTS 1", expts, flush=True)
gl_list, rgs_list, bin_list, tglrs_list = cycle_thru_expts(dates, expts, enss, ddir=ddir, mp_expt=True, mp_date=False, SAT='ALL')
print("FINISHED CYCLE THROUGH ALL EXPERIMENT DATES mp_expt=True", flush=True)

print("PROCESS EXPTS 2", expts)
gl_list, rgs_list, bin_list, tglrs_list = cycle_thru_expts(dates, expts, enss, ddir=ddir, mp_expt=False, mp_date=True, SAT='ALL')
print("FINISHED CYCLE THROUGH ALL EXPERIMENT DATES mp_expt=False", flush=True)

EOD
