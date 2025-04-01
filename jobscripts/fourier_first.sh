#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/fourier_first.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/fourier_first.sh -d=CCYYMMDD

## DEFAULTS
SLOW=False

## GET arguments
for i in "$@"
do
case $i in
    -d=*|--date=*)
    DATE="${i#*=}"
    shift # past argument=value
    ;;
    -s|--slow)
    SLOW=True
    shift # past argument=value
    ;;
esac
done
if [[ -z ${DATE} ]]; then
   echo "DATE required"
   echo ${USAGE}
   exit 99
fi
if [[ ${#DATE} -lt 8 ]] ; then
   echo "DATE CCYYMMDD required"
   echo $USAGE
   exit 99
fi
DATE=${DATE:0:8}

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

#for VAR in SST T SSU SSV MLD U15 V15 TAUX TAUY Tsppt Ssppt; do 
#for VAR in TAUX TAUY ; do 
for VAR in R75 ; do 

BJOB=/home/dpe000/EnGIOPS/JOBS/fourier_${VAR}_${DATE}_${SLOW:0:1}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/fourier_${VAR}_${DATE}_${SLOW:0:1}.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python ${PJOB}

EOB

cat > ${PJOB} << EOP

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import datetime
import check_date

import fourier_analysis

slow=${SLOW}
date=check_date.check_date(${DATE}, outtype=datetime.datetime)
if ( slow ):
    kwave, PSA_list, PSB_list = fourier_analysis.box_cycle(date=date, var='${VAR}')
else:
    kwave, PSA_list, PSB_list = fourier_analysis.box_cycle_fast(date=date, var='${VAR}')
 
print('kwave')
print(kwave)

EOP

${SJOB}

done

