#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_scatter.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in T U; do 

BJOB=${WDIR}/JOBS/plot_scatter_${EX}.sh
PJOB=${WDIR}/JOBS/plot_scatter_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

cat > ${BJOB} << EOB
echo HOST=\$(hostname)

cd ${WDIR}
export MPLBACKEND=agg
#source /home/dpe000/GEOPS/jobscripts/preconda.sh
#source activate metcarto
source  /home/dpe000/EnGIOPS/jobscripts_drew/prepython.sh

python ${PJOB}

EOB

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
rank_histogram.plot_scatter_in_range('${EX}FIG/','GIOPS_${EX}', [20210505, 20211201])

EOP

${SJOB}

done
