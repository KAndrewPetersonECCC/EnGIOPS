#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/test_common.sh -cpus 1 -mpi -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts_drew/prepython.sh

python << EOD

import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram
import find_common

tdate=datetime.datetime(2021,12,1)
expt='GIOPS_T'

DF_list = rank_histogram.read_IS_ensemble(expt, tdate)
for sat_id in [13, 15, 17, 18]:
    print('setID', sat_id)
    DF_subl = rank_histogram.subset_DF_LIST(DF_list, 'setID', sat_id)
    print('setID', sat_id, [ len(DF) for DF in DF_subl])
    NF_list = find_common.find_common(DF_subl)

EOD
