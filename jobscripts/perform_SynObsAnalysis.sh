#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/perform_SynObsAnalysis.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

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
import check_date
import find_cspeed_maxmin
import read_EN4
import soundspeed
import numpy as np
import find_value_at_point
import read_grid
import rank_histogram

syndir='/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs' 

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)

dates=rank_histogram.create_dates(20200101, 20221231, 1)

keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOTS', filesuf='3years', levels=levels, ticks=ticks)


keylist=['Oper', 'CNTLV2', 'Free', 'NoAltV2']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOT1', filesuf='3years', levels=levels, ticks=ticks)

dates=rank_histogram.create_dates(20200101, 20221220, 1)

keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBSE3/', pdir='CSPEED/SYNOBSE3/PLOTS', filesuf='3years', levels=levels, ticks=ticks)


keylist=['Oper', 'CNTLV2', 'Free', 'NoAltV2']
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBSE3/', pdir='CSPEED/SYNOBSE3/PLOT1', filesuf='3years', levels=levels, ticks=ticks)
EOD
