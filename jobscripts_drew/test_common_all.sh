#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/test_common_all.sh -share e -cpus 40 -cm 187000M -t 21600 -shell=/bin/bash
#qsub -lselect=1:ncpus=10:mem=128000M -lplace=scatter -qdevelopment -lwalltime=6:0:0 /home/dpe000/EnGIOPS/jobscripts_drew/test_common_all.sh 

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source /home/dpe000/EnGIOPS/jobscripts_drew/prepython.sh

python << EOD

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
import pickle

print( 'NUM_CPUS = ', len(os.sched_getaffinity(0)) )

tdate=datetime.datetime(2021,12,1)
sdate=rank_histogram.check_date(tdate, dtlen=8)
expt='GIOPS_T'

DF_list = rank_histogram.read_IS_ensemble(expt, tdate, mp=True)
NF_list = find_common.find_common_by_Tstp(DF_list, mp=True)

direname='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0'
filename=direname+'/DRU2/'+'OLA_IS.'+sdate+'.pkl'

with open(filename,'wb') as fp:
    pickle.dump(NF_list,fp)

with open(filename,'rb') as fp:
    NN_LIST=pickle.load(fp)


EOD
