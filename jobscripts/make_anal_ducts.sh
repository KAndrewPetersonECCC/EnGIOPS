#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_ducts.sh -cpus 40 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/test_ducts.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

source /home/dpe000/HPCARCHIVE/DATES.source

for DATE in ${ALL_2021_DATES} ${ALL_2022_DATES} ; do 

BJOB=/home/dpe000/EnGIOPS/JOBS/make_duct_${DATE}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/test_duct_${DATE}.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${PJOB} << EOP
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin

find_cspeed_maxmin.do_ducts_for_cycle(${DATE})
EOP

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python ${PJOB}

EOB

${SJOB}

done
