#!/bin/bash 
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_ratios_loop.sh

TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
DDIR=/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives
date=20201104

## GET arguments
for i in "$@"
do
case $i in
    -s=*|--start=*)
    SDATE="${i#*=}"
    shift # past argument=value
    ;;
    -f=*|--final=*)
    FDATE="${i#*=}"
    shift # past argument=value
    ;;
    -p=*|--plot=*)
    PLOT="${i#*=}"
    shift # past argument=value
    ;;
esac
done
if [[ -z ${SDATE} ]]; then
   echo "SDATE required"
   echo ${USAGE}
   exit 99
fi
if [[ -z ${FDATE} ]]; then
   echo "FDATE required"
   echo ${USAGE}
   exit 99
fi
if [[ ${#SDATE} -lt 8 ]] ; then
   echo "DATE CCYYMMDD required"
   echo $USAGE
   exit 99
fi
if [[ ${#FDATE} -lt 8 ]] ; then
   echo "DATE CCYYMMDD required"
   echo $USAGE
   exit 99
fi
SDATE=${SDATE:0:8}
FDATE=${SDATE:0:8}

if [[ -z ${PLOT} ]]; then
   echo "PLOT required"
   echo ${USAGE}
   exit 99
fi

cd ${TDIR}
if [[ $? -ne 0 ]] ; then 
   echo "Cannot reach ${TDIR}"
   exit 99
fi

mkdir /fs/site3/eccc/mrd/rpnenv/dpe000/EnGIOPS/${PLOT}
ln -s /fs/site3/eccc/mrd/rpnenv/dpe000/EnGIOPS/${PLOT} .
PJOB=${TDIR}/JOBS/produce_ensemble_ratios_loop.${PLOT}.${SDATE}_${FDATE}.py
BJOB=${TDIR}/JOBS/produce_ensemble_ratios_loop.${PLOT}.${SDATE}_${FDATE}.sh
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

cd ${TDIR}
export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto
python ${PJOB}
exit 0
EOB

cat > $PJOB << EOP
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime

import read_dia
import datadatefile

datestrs='${SDATE}'
datestrf='${FDATE}'
daterange=[ datadatefile.convert_strint_date(datestrs), datadatefile.convert_strint_date(datestrf)]
read_dia.loop_calc_ratio(daterange, pdir='${PLOT}')

EOP

${SJOB}
