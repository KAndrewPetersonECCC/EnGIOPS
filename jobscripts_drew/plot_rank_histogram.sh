#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_rank_histogram.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in T U C; do 

BJOB=${WDIR}/JOBS/plot_rank_${EX}.sh
PJOB=${WDIR}/JOBS/plot_rank_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

cat > ${BJOB} << EOB

echo HOST=\$(hostname)
WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
#source /home/dpe000/GEOPS/jobscripts/preconda.sh
#source activate metcarto
source  /home/dpe000/EnGIOPS/jobscripts_drew/prepython.sh


python ${PJOB}

EOB

PYC="rank_histogram.plot_rank_over_range('${EX}FIG/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21)"
if [[ ${EX} == A ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('PLOTS/EXPA', ['GIOPS_E', 'GIOPS_T', 'GIOPS_Q'], date_range, obstype='DS',enn=21)"
fi
if [[ ${EX} == B ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('PLOTS/EXPB', ['GIOPS_E', 'GIOPS_S', 'GIOPS_P'], date_range, obstype='DS',enn=21)"
fi
if [[ ${EX} == C ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('PLOTS/EXPC', ['GIOPS_T', 'GIOPS_U'], date_range, obstype='DS',enn=21)"
fi


cat > ${PJOB} << EOP
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

plt.rc('text', usetex=False)

date_range=[20210505,  20211201]
${PYC}
EOP

${SJOB}

done

