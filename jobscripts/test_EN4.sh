#!/bin/bash -x
#test_EN4.sh

source jobscripts/prepython.sh 

python << EOD
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin
import read_ensemble_forecast
import datetime
import pytz
import soundspeed
import numpy as np
import read_EN4
import read_grid
import find_value_at_point
import time

lonn, latn, orca_area = read_grid.read_coord()

LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(2001,1,15)
LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_month(2001,1)
#LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_months(2022, list(range(1,13)))
#LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(2001,1,15)
IBTH=read_EN4.find_both_valid_TS(QT, QS)
LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IBTH)
IDEP=read_EN4.remove_minimum_depth(DEP, QT, min_depth=100.0)
LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IDEP)

CW = soundspeed.sound_speed(DEP, SW, TW)
mp=True # for years worth of profiles -- and then only factor of 2.
tim0=time.time() ; TorF_mist = find_cspeed_maxmin.find_mins_obs(CW, DEP, mp=True); print('mp find_mins', time.time()-tim0)
tim0=time.time() ; TorF_list = find_cspeed_maxmin.find_mins_obs(CW, DEP, mp=False); print('sq find_mins',time.time()-tim0)

tim0=time.time(); IJPTS=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=False); print('sq find_pts',time.time()-tim0)
tim0=time.time(); IJPTM=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=True); print('mp find_pts',time.time()-tim0)

EOD

