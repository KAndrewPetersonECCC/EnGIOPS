#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/plot_SynOBS.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/plot_SynOBS.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD


from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import time
import datetime
import check_date
import find_cspeed_maxmin
import read_EN4
import soundspeed
import numpy as np
import find_value_at_point
import read_grid
import rank_histogram


dates=rank_histogram.create_dates(20200101, 20221231, 1)
keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
#find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOTS', filesuf='3years', levels=levels, ticks=ticks)

dates=rank_histogram.create_dates(20200108, 20210615, 1)+rank_histogram.create_dates(20210825, 20211109, 1)
keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV2', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV2', 'NoAltV2']

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
#find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBSE2/', pdir='CSPEED/SYNOBSE2/PLOTS', filesuf='2021', levels=levels, ticks=ticks)

keylist=['Oper', 'CNTLV2', 'Free', 'NoAltV2']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='Oper', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOT2', filesuf='all_dates', levels=levels, ticks=ticks)

dates=rank_histogram.create_dates(20200101, 20221231, 1)
keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBS4/', pdir='CSPEED/SYNOBS4/PLOTS', filesuf='all_dates', levels=levels, ticks=ticks)



keylist=['IC4', 'CTL']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
#find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='CTL', keylist=keylist, ddir='CSPEED/IC4_A/', pdir='CSPEED/IC4_A/PLOTS', filesuf='all_dates', levels=levels, ticks=ticks)

keylist=['IC4', 'CTL', 'IC4_l', 'CTL_l']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
#find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='CTL_l', keylist=keylist, ddir='CSPEED/IC4_B/', pdir='CSPEED/IC4_B/PLOTS', filesuf='all_dates', levels=levels, ticks=ticks)

EOD
