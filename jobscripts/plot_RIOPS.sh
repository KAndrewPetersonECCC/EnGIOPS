#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_RIOPS.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/plot_RIOPS.sh

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


keylist=['RIOPS', 'GIOPS', 'RIOPS_l', 'GIOPS_l']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)

find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='GIOPS', keylist=keylist, ddir='CSPEED/RIOPS', pdir='CSPEED/RIOPS/PLOTS/', filesuf='all_dates', levels=levels, ticks=ticks)


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
