#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/work_SSH_OLA.sh -cpus 80 -cm 64000M -t 21600 -shell=/bin/bash

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

dates = rank_histogram.create_dates(20210602, 20220525, 7)
expts=('GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T')
labels=('Ensemble', 'Operation', 'Control')
enss=(21, 0, 1)
ddir=[read_DF_VP.get_mdir(5,user='dpe000')]*3
outdir=[expt for expt in expts]
outdir=['GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T0']
LEV1 = np.arange(0, 0.21, 0.02)
LEV2 = np.arange(-0.19, 0.2, 0.02)
LEV3 = np.arange(-0.09, 0.1, 0.02)
read_DF_IS.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre='ECMP_', NP=20, LEV_posd=LEV1, LEV_anom=LEV2, LEV_diff=LEV3)
EOD
