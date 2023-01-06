#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_rank_histogram.sh -cpus 1 -mpi -cm 8000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

#for EX in G5a G5b G5c; do 
for EX in G5b; do 

BJOB=${WDIR}/JOBS/plot_rank_${EX}.sh
PJOB=${WDIR}/JOBS/plot_rank_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 80 -mpi -cm 2000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB

echo HOST=\$(hostname)
WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
#source /home/dpe000/GEOPS/jobscripts/preconda.sh
#source activate metcarto
source  /home/dpe000/EnGIOPS/jobscripts/prepython.sh


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
if [[ ${EX} == G5a ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('T1/G5.DO', ['GIOPS_T'], date_range_G5, obstype='DS',enn=21, groupby=False)"
fi
if [[ ${EX} == G5b ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('T1/G5.DS', ['GIOPS_T'], date_range_G5, obstype='DS',enn=21, groupby=True)"
fi
if [[ ${EX} == G5c ]] ; then 
PYC="rank_histogram.plot_ranks_over_range('T1/G5.IS', ['GIOPS_T'], date_range_G5, obstype='IS',enn=21, groupby=True)"
fi


cat > ${PJOB} << EOP
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

plt.rc('text', usetex=False)

date_range=[20210505,  20211201]
date_range_G5=[20210602, 20220601]
${PYC}
EOP

${SJOB}

done

