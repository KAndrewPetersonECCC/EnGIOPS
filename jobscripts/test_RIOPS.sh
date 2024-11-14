#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_ducts.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/test_ducts.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

BJOB=/home/dpe000/EnGIOPS/JOBS/test_duct.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/test_duct.py
OJOB=/home/dpe000/EnGIOPS/python/find_cspeed_tmp.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${PJOB} << EOP
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin




EOP

##SUPERSEED
cat ${OJOB} > ${PJOB}

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
cat ${OJOB} > ${PJOB}
python ${PJOB}

EOB

${SJOB}
