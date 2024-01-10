#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/work3_SSH_OLA.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

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
import read_DF_VP
import rank_histogram
import read_DF_IS

print("PROCESS EXPERIMENT", flush=True)
dates = rank_histogram.create_dates(20210602, 20220601, 7)
# NP=20 seems the largest that works.   GOOD news, it still does 53 dates in about 1 hour.
expt, gl_series_avg, rgs_series_avg, bin_series_avg, tglrs_series = read_DF_IS.process_expt(dates, 'GIOPS_T', list(range(21)), read_DF_VP.get_mdir(5), mp_read=False, mp_date=True, SAT='ALL', NP=20)
print("FINISH PROCESS EXPERIMENT", flush=True)

EOD
