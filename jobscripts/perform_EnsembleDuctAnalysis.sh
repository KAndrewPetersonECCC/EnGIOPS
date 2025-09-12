#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/perform_EnsembleDuctAnalysis.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python << EOD


#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import time
import datetime
import numpy as np
import check_date
import find_cspeed_maxmin
import rank_histogram

dates=rank_histogram.create_dates(20210601, 20220531, 1)
#find_cspeed_maxmin.calc_class4_duct_stats(dates, filesuf='20210601_20220531')

levels=np.arange(-0.475, 0.5, 0.05)
ticks=np.arange(-0.4, 0.50, 0.1)


keylist=['GEPS', 'GEP0', 'GDPS', 'GLAG', 'GCLM']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='GCLM', keylist=keylist, ddir='CSPEED/CLASS4/', pdir='CSPEED/CLASS4/PLOTS_CLM', filesuf='1year', levels=levels, ticks=ticks)

keylist=['GEPS', 'GEP0', 'GDPS', 'GLAG', 'GCLM']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='GDPS', keylist=keylist, ddir='CSPEED/CLASS4/', pdir='CSPEED/CLASS4/PLOTS_GDP', filesuf='1year', levels=levels, ticks=ticks)

keylist=['GEPS', 'GEP0', 'GDPS', 'GLAG', 'GCLM']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='GEPS', keylist=keylist, ddir='CSPEED/CLASS4/', pdir='CSPEED/CLASS4/PLOTS_GEP', filesuf='1year', levels=levels, ticks=ticks)

EOD

