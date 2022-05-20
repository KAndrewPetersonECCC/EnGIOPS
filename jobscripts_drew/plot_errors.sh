#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_errors.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in E T Q S P ; do

BJOB=${WDIR}/JOBS/plot_errors_${EX}.sh
PJOB=${WDIR}/JOBS/plot_errors_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

cat > ${BJOB} << EOB
WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto

python ${PJOB}

EOB

cat > ${PJOB} << EOP

import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

rank_histogram.plot_errors_over_range('${EX}FIG/', 'GIOPS_${EX}', [20200101,  20201230], obstype='DS', enn=21)

EOP
