#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_errors.sh -cpus 1 -mpi -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in T ; do

HOST=$(hostname | cut -c -4)
BJOB=${WDIR}/JOBS/plot_errors_${EX}.sh
PJOB=${WDIR}/JOBS/plot_errors_${EX}.py
LOGF=/home/dpe000/listings/plot_errors_${EX}.log
echo ${LOGF}
SJOB="ord_soumet ${BJOB} -cpus 80 -mpi -cm 2000M -t 21600 -shell=/bin/bash"
SJOB="qsub -lselect=1:ncpus=80:mem=184G -lplace=scatter -qdevelopment -lwalltime=6:0:0 -o ${LOGF} ${BJOB}"

echo HOST=$(hostname)
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

cat > ${PJOB} << EOP

import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import rank_histogram

date_range= [20210602,  20220601]
plt.rc('text', usetex=False)
#[avg_misfit1, avg_squerr1, avg_errvar1, avg_tsqerr1, avg_crps1] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}1/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21, groupby=True, bin1st=False)
#[avg_misfit2, avg_squerr2, avg_errvar2, avg_tsqerr2, avg_crps2] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}2/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21, bin1st=True)
#[avg_misfit3, avg_squerr3, avg_errvar3, avg_tsqerr3, avg_crps3] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}3/', 'GIOPS_${EX}', date_range, obstype='DS', enn=21, groupby=False, bin1st=False)

#print(np.min(avg_misfit1 - avg_misfit2),  np.max(avg_misfit1 - avg_misfit2) )
#print('CHECK', np.min(avg_misfit1 - avg_misfit3),  np.max(avg_misfit1 - avg_misfit3) )

CLEVA=np.arange(-0.09, 0.11, 0.02)
CLEVF=np.arange(0, 0.11, 0.01)
[avg_misfit1, avg_squerr1, avg_errvar1, avg_tsqerr1, avg_crps1] , [grid_lon, grid_lat] = rank_histogram.plot_errors_over_range('${EX}1/', 'GIOPS_${EX}', date_range, obstype='IS', enn=21, groupby=True, bin1st=False, clev_full=CLEVF, clev_anom=CLEVA)

EOP
${SJOB} 

done
