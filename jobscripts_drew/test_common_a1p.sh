#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/test_common_a1p.sh -cpus 1 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts_drew/prepython.sh

python << EOD

#from importlib import reload

from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram
import find_common

print( 'NUM_CPUS = ', len(os.sched_getaffinity(0)) )

tdate=datetime.datetime(2021,12,1)
expt='GIOPS_T'

DF_list = rank_histogram.read_IS_ensemble(expt, tdate, mp=False)
NF_list = find_common.find_common_by_Tstp(DF_list, mp=False)

EOD
