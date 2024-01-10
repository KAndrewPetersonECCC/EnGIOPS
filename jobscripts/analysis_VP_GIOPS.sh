#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_GIOPS.sh -cpus 20 -cm 64000M -t 21600 -shell=/bin/bash

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


dates = rank_histogram.create_dates(20210602, 20220601, 7)

expts=('GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T')
labels=('Ensemble', 'Operation', 'Control')
enss=(21, 0, 1)
ddir=[read_DF_VP.get_mdir(5,user='dpe000')]*3
outdir=[expt for expt in expts]
outdir=['GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T0']
read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre='ECMP_')
EOD
