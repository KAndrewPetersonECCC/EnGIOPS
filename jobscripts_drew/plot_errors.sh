#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_errors.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in T U ; do

BJOB=${WDIR}/JOBS/plot_errors_${EX}.sh
PJOB=${WDIR}/JOBS/plot_errors_${EX}.py
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

echo HOST=$(hostname)
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

cat > ${PJOB} << EOP

import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

date_range= [20211103,  20211201]
plt.rc('text', usetex=False)
[avg_misfit1, avg_squerr1, avg_errvar1] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}1/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21, bin1st=False)
[avg_misfit2, avg_squerr2, avg_errvar2] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}2/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21, bin1st=True)
[avg_misfit3, avg_squerr3, avg_errvar3] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}3/', 'GIOPS_${EX}', date_range, obstype='IS', enn=21, bin1st=True)

print(np.min(avg_misfit1 - avg_misfit2),  np.max(avg_misfit1 - avg_misfit2) )
print(np.min(avg_squerr1 - avg_squerr2),  np.max(avg_squerr1 - avg_squerr2) )
print(np.min(avg_errvar1 - avg_errvar2),  np.max(avg_errvar1 - avg_errvar2) )


EOP
${SJOB} 

done
