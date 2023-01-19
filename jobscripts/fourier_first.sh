#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/fourier_first.sh -cpus 1 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/fourier_first.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for VAR in SST T SSU SSV MLD U15 V15 D20 ; do 

BJOB=/home/dpe000/EnGIOPS/JOBS/fourier_${VAR}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/fourier_${VAR}.py
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

import fourier_analysis
#import rank_histogram
#fourier_analysis.test_cycle(var='${VAR}')
kvals, Mbins, Ebins, Mbins_list, Ebins_list = fourier_analysis.box_cycle(var='${VAR}')

print('KVALS')
print(kvals)
print('MBINS')
print(Mbins)

EOP

${SJOB}

done

