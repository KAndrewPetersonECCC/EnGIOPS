#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_XX.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#time bash /home/dpe000/EnGIOPS/jobscripts/test_XX.sh

cd /home/dpe000/EnGIOPS/
source jobscripts/prepython.sh

python << EOD
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin
import read_ensemble_forecast
import datetime
import find_cspeed_maxmin
import soundspeed
import numpy as np

#S, lat, lon, lev   = read_ensemble_forecast.read_ensemble_forecast('S', 'E1Y25EP1', datetime.datetime(2019,7,1), 24, #ddir='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives')
#T, lat, lon, lev   = read_ensemble_forecast.read_ensemble_forecast('T', 'E1Y25EP1', datetime.datetime(2019,7,1), 24,  ##ddir='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives')
#TC = [soundspeed.Kelvin_to_Celsius(Te) for Te in T]
#C = find_cspeed_maxmin.calc_sound_speed_ensemble(TC, S, lev, mp_ensemble=True)

#T, lat, lon, lev   = read_ensemble_forecast.read_ensemble_forecast('T', 'oper', datetime.datetime(2023,5,12), 24,  ddir='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives')

hir6=find_cspeed_maxmin.hir6  # maestro_hpcarchive on site6

#find_cspeed_maxmin.do_ducts_for_fcstdate(2019062200, expt='E1Y25EP1', mindepth=10.0, maxdepth=100.0, ddir=hir6, pdir='CSPEED/E1Y25EP1')
find_cspeed_maxmin.do_ducts_for_fcstdate(2023052500, expt='oper', mindepth=10.0, maxdepth=100.0, ddir=hir6, pdir='CSPEED/GEPSOPER')
find_cspeed_maxmin.do_ducts_for_fcstdate(2023051800, expt='oper', mindepth=10.0, maxdepth=100.0, ddir=hir6, pdir='CSPEED/GEPSOPER')
EOD
