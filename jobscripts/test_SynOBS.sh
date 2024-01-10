#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_SynOBS.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

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

syndir='/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs' 
date=check_date.check_date(20200101, outtype=datetime.datetime)  
dateint=int(datestr)
datestr=check_date.check_date(date, outtype=str)
dateint=int(datestr)
adate = date + datetime.timedelta(days=1)
YY, MM, DD = date.year, date.month, date.day

LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(YY,MM,DD)
anal_date, anal_diff = find_cspeed_maxmin.find_nearest_analysis(adate)
IBTH=read_EN4.find_both_valid_TS(QT, QS)
LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IBTH)
IDEP=read_EN4.remove_minimum_depth(DEP, QT, min_depth=100.0)
LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.replace_list_of_array([LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS], IDEP)
CW = soundspeed.sound_speed(DEP, SW, TW)
TorF_list = find_cspeed_maxmin.find_mins_obs(CW, DEP, mp=False)  
TorF_narr = np.array(TorF_list).astype(int)
lonn, latn, orca_area = read_grid.read_coord()
IJPTS=find_value_at_point.find_nearest_point_list(LON, LAT, lonn, latn, mp=False)

__, __, Pctrl, __ = find_cspeed_maxmin.find_ducts_for_date(adate, anal=False, expt='CNTL', ddir=syndir, ensembles='d')
__, __, PNoArgo, __ = find_cspeed_maxmin.find_ducts_for_date(adate, anal=False, expt='NoArgo', ddir=syndir, ensembles='d')
__, __, PNoSST, __ = find_cspeed_maxmin.find_ducts_for_date(adate, anal=False, expt='NoSST', ddir=syndir, ensembles='d')

Nmask = read_grid.read_mask()[0]
Probs, BRSCs, SPRDs = find_cspeed_maxmin.calc_class4_duct_SYNOBS(check_date.check_date(20200101,outtype=datetime.datetime))

date=datetime.datetime(2020,1,8)
find_cspeed_maxmin.calc_class4_duct_SYNOBS_cycle(date)

date=datetime.datetime(2020,1,8)
date=datetime.datetime(2021,6,9)
find_cspeed_maxmin.calc_class4_duct_cycle(date)


dlist=['/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle']
keylist=['GX35FCH22V2', 'IC4GX340EH22-CTR']
ddict = dict(zip(keylist, dlist))       
#Probs, BRSCs, SPRDs = find_cspeed_maxmin.calc_class4_duct_SYNOBS(check_date.check_date(20220101,outtype=datetime.datetime), keylist=keylist, dirlist=dlist, odir='CSPEED/IC4_A')
find_cspeed_maxmin.calc_class4_duct_SYNOBS_cycle(check_date.check_date(20220115,outtype=datetime.datetime), keylist=keylist, dirlist=dlist, odir='CSPEED/IC4_A')

dlist=['/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle', '/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle']
keylist=['IC4','CTL','IC4_l', 'CTL_l']
explist=['GX35FCH22V2', 'IC4GX340EH22-CTR','GX35FCH22V2', 'IC4GX340EH22-CTR']
enslist=['d','d','l','l']
ddict = dict(zip(keylist, dlist))       
#Probs, BRSCs, SPRDs = find_cspeed_maxmin.calc_class4_duct_SYNOBS(check_date.check_date(20220101,outtype=datetime.datetime), keylist=keylist, explist=explist, dirlist=dlist, enslist=enslist, odir='CSPEED/IC4_B')
find_cspeed_maxmin.calc_class4_duct_SYNOBS_cycle(check_date.check_date(20220105,outtype=datetime.datetime), keylist=keylist, explist=explist, dirlist=dlist, enslist=enslist, odir='CSPEED/IC4_B')


dates=rank_histogram.create_dates(20200101, 20221231, 1)
keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOTS', filesuf='3years', levels=levels, ticks=ticks)

dates=rank_histogram.create_dates(20200108, 20210615, 1)+rank_histogram.create_dates(20210825, 20211109, 1)
keylist=['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV2', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV2', 'NoAltV2']

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(dates, reference='CNTLV2', keylist=keylist, ddir='CSPEED/SYNOBSE2/', pdir='CSPEED/SYNOBSE2/PLOTS', filesuf='2021', levels=levels, ticks=ticks)

keylist=['Oper', 'CNTLV2', 'Free', 'NoAltV2']

levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='Oper', keylist=keylist, ddir='CSPEED/SYNOBS3/', pdir='CSPEED/SYNOBS3/PLOT1', filesuf='all_dates', levels=levels, ticks=ticks)

keylist=['IC4', 'CTL']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='CTL', keylist=keylist, ddir='CSPEED/IC4_A/', pdir='CSPEED/IC4_A/PLOTS', filesuf='all_dates', levels=levels, ticks=ticks)

keylist=['IC4', 'CTL', 'IC4_l', 'CTL_l']
levels=np.arange(-0.095, 0.1, 0.01)
ticks=np.arange(-0.09, 0.10, 0.02)
find_cspeed_maxmin.calc_class4_duct_stats_key(None, reference='CTL_l', keylist=keylist, ddir='CSPEED/IC4_B/', pdir='CSPEED/IC4_B/PLOTS', filesuf='all_dates', levels=levels, ticks=ticks)

EOD
