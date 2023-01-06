#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_profiles.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash  /home/dpe000/EnGIOPS/jobscripts/test_profiles.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for YR in 2020 2021; do 
for MP in True False ; do 

BJOB=/home/dpe000/EnGIOPS/JOBS/test_profiles_${YR}.${MP:0:1}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/test_profiles_${YR}.${MP:0:1}.py
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

import find_profile_test
find_profile_test.find_profile(years=[${YR}], mp_system=${MP})

EOP

${SJOB}

done
done
