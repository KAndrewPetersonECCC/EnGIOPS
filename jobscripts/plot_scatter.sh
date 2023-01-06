#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_scatter.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for EX in T; do 
for TY in DS IS DO ; do 

BJOB=${WDIR}/JOBS/plot_scatter_${EX}_${TY}.sh
PJOB=${WDIR}/JOBS/plot_scatter_${EX}_${TY}.py
SJOB="ord_soumet ${BJOB} -cpus 80 -mpi -cm 2000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB
echo HOST=\$(hostname)

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

plt.rc('text', usetex=False)
if ( '${TY}' == 'DS' ):
    obstype='DS'
    obserr=0.3
    groupby=True
    odir='${EX}1/'
elif ( '${TY}' == 'DO' ):
    obstype='DS'
    obserr=0.3
    groupby=False
    odir='${EX}3/'
elif ( '${TY}' == 'IS' ):
    obstype='IS'
    obserr=0.1
    groupby=True
    odir='${EX}1/'
    
rank_histogram.plot_scatter_in_range('${EX}1/','GIOPS_${EX}', [20210602, 20220601],obstype=obstype, obs_err=obserr)

EOP

${SJOB}

done
done
