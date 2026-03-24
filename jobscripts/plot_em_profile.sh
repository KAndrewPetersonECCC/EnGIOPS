!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_em_profile.sh -cpus 60 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/plot_em_profile.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/new_python.sh

python << EOP
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import subprocess

import monitor_VP


expt='gx_EF1.0'
date_range=[20220601, 20220928]
plotto='PLOTS_EF1.0/'
plottB='PLOTS_EF1.0B/'

expt='gx_EE1.0'
date_range=[20200101, 20200520]
plotto='PLOTS_EE1.0/'
plottB='PLOTS_EE1.0B/'


rc=subprocess.call(['mkdir','-p', plottB])
monitor_VP.global_mean_profile2(expt, date_range, ref='gx4_a3.1', group='VP/VP_GEN_PR_PF', plotto=plottB)
print("END QUICK", flush=True)

rc=subprocess.call(['mkdir','-p', plotto])
monitor_VP.global_mean_profile(expt, date_range, ref='gx4_a3.1', group='VP/VP_GEN_PR_PF', plotto=plotto)
print("END SLOW", flush=True)

EOP
