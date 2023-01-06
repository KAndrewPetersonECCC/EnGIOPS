#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_graig.sh -cpus 20 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

#from multiprocessing import set_start_method
#set_start_method("spawn")
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

FULL_dates = rank_histogram.create_dates(20190313, 20200401, 7)
TRUN_dates = rank_histogram.create_dates(20190501, 20200401, 7)

expts=('gx_dev-3.4.0_sbcwave_gls', 'gx_dev-3.4.0_sbcwave')
labels=('GLS', 'GX')
outdir=('GLS', 'GX')
enss=(0, 0)

read_DF_VP.produce_stats_plot( FULL_dates, expts, enss, labels=labels, outdir=outdir, ddir='/fs/site5/eccc/mrd/rpnenv/gsu000/maestro_archives/giops', mp_expt=True, mp_read=False)
read_DF_VP.produce_stats_plot( TRUN_dates, expts, enss, labels=labels, outdir=outdir, ddir='/fs/site5/eccc/mrd/rpnenv/gsu000/maestro_archives/giops', mp_expt=True, mp_read=False)
print("FINISHED")

EOD
