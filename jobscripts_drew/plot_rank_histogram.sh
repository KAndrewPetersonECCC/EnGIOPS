#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_rank_histogram.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in E T Q S P A B; do 

BJOB=${WDIR}/JOBS/plot_rank_${EX}.sh
PJOB=${WDIR}/JOBS/plot_rank_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

cat > ${BJOB} << EOB

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto

python ${PJOB}

EOB

PYC="rank_histogram.plot_rank_over_range('${EX}FIG/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21)"
if [[ ${EX} == A ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('PLOTS/EXPA', ['GIOPS_E', 'GIOPS_T', 'GIOPS_Q'], date_range, obstype='DS',enn=21)"
fi
if [[ ${EX} == B ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('PLOTS/EXPB', ['GIOPS_E', 'GIOPS_S', 'GIOPS_P'], date_range, obstype='DS',enn=21)"
fi


cat > ${PJOB} << EOP
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

date_range=[20200101,  20200129]
date_range=[20200101,  20201230]
${PYC}
EOP

${SJOB}

done

