#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_test.sh -cpus 20 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
mpl.use('Agg')
import time
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

THE_dates = rank_histogram.create_dates(20210602, 20210630, 7)

expts=('GIOPS_T', 'GIOPS_330_GD')
labels=('Ensemble', 'Operation')
outdir=('ENSEMBLE', 'OPERATION')
enss=(21, 0)

IDO = 2

TrFl = ( (False, False), (False, True), (True, False), (True, True) )

mp_expt, mp_read = TrFl[IDO]

print("STARTING MP: SETTINGS:  mp_expt = ", mp_expt, " mp_read = ", mp_read)
time0=time.time()
gl_list, rgs_list, bin_list, grgs_list = read_DF_VP.cycle_thru_expts(THE_dates, expts, enss, mp_expt=mp_expt, mp_read=mp_read)
timeF = time.time() - time0
print("FINISHED MP: SETTINGS:  mp_expt = ", mp_expt, " mp_read = ", mp_read)
print("FINISHED MP:  Exectution TIME ", timeF)

EOD
