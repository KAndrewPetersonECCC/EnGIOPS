#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_spread.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/plot_spread.sh 

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

for VAR in T S U V; do

BJOB=/home/dpe000/EnGIOPS/JOBS/plot_spread_${VAR}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/plot_spread_${VAR}.py
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

import plot_spread
import create_dates

expt='dev-4.0.0.ensembles_CTL'
leads = np.arange(24,169,24)
dates = create_dates.create_dates(20211013, 20220921,7)

glbvar, glbmne = plot_spread.cycle_thru_leads_date(expt, dates, leads, var='${VAR}', mp_loop=True)

EOP

${SJOB}

done

