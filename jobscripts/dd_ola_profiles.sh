#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/dd_ola_profiles.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/dd_ola_profiles.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

BJOB=/home/dpe000/EnGIOPS/JOBS/dd_ola_profiles.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/dd_ola_profiles.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python3 ${PJOB}
EOB


cat > ${PJOB} << EOP
#from importlib import reload
import sys
#import os

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import plot_xrola_profiles
plot_xrola_profiles.do_profiles()
                            
EOP

${SJOB}
