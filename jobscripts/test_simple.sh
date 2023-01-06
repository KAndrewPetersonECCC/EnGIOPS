#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_simple.sh -cpus 40 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram
import find_common

tdate=datetime.datetime(2021,12,1)
expt='GIOPS_T'

print( 'NUM_CPUS = ', len(os.sched_getaffinity(0)) )
sys.stdout.flush()

DF_list = rank_histogram.read_IS_ensemble(expt, tdate, mp=True)

DS_LIST = rank_histogram.read_DS_ensemble(expt, tdate, mp=True)

EOD
