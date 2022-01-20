#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh

TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
date=20201104

## GET arguments
for i in "$@"
do
case $i in
    -d=*|--date=*)
    DATE="${i#*=}"
    shift # past argument=value
    ;;
esac
done
if [[ -z ${DATE} ]]; then
   echo "DATE required"
   echo ${USAGE}
   exit 99
fi

cd ${TDIR}
if [[ $? -ne 0 ]] ; then 
   echo "Cannot reach ${TDIR}"
   exit 99
fi

PJOB=${TDIR}/JOBS/produce_ensemble_plots.${DATE}.py
BJOB=${TDIR}/JOBS/produce_ensemble_plots.${DATE}.sh
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

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

datestr='${DATE}'
date=datadatefile.convert_strint_date(datestr)
read_dia.plot_date(date)

EOP

${SJOB}
