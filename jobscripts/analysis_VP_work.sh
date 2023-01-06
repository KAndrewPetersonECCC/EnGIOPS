#!/bin/bash -x
#DONT : ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_work.sh -cpus 20 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

from importlib import reload
#from multiprocessing import set_start_method
#set_start_method("spawn")
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

dates = rank_histogram.create_dates(20210602, 20210630, 7)
dates = rank_histogram.create_dates(20211103, 20211124, 7)

gl_series, rgs_series, bin_series, grgs_varray = read_DF_VP.cycle_thru_dates(dates, 'GIOPS_T')
gld_series, rgsd_series, bind_series, grgsd_varray = read_DF_VP.cycle_thru_dates(dates, 'GIOPS_330_GD', deterministic=True)
glc_series, rgsc_series, binc_series, grgsc_varray = read_DF_VP.cycle_thru_dates(dates, 'GIOPS_T', ens=[0])

read_DF_VP.plot_profiles_multi((gl_series, gld_series, glc_series), ('Ensemble', 'Operation', 'Control'))

gl_single, rgs_single, bin_single = read_DF_VP.calc_errors_date(20210602, 'GIOPS_T')  
gl_daily, rgs_daily = read_DF_VP.apply_averaging(gl_single, rgs_single)

read_DF_VP.plot_profiles(gl_single)

gld_single, rgsd_single, bind_single = read_DF_VP.calc_errors_date(20210602, 'GIOPS_330_GD', deterministic=True)  
gld_daily, rgsd_daily = read_DF_VP.apply_averaging(gld_single, rgsd_single)

gld_single = read_DF_VP.final_mean_list(gld_single)
rgsd_single = read_DF_VP.final_mean_list(rgsd_single)
bind_single = read_DF_VP.final_mean_list(bind_single)

gld_daily, rgs

dates = rank_histogram.create_dates(20210602, 20210630, 7)

expts=('GIOPS_T', 'GIOPS_330_GD', 'GIOPS_T')
labels=('Ensemble', 'Operation', 'Control')
enss=(21, 0, 1)
read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outpre='PLOTS/ECMP')

EOD
