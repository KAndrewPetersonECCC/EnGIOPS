from importlib import reload
import sys
import os
import time

import numpy as np
import datetime
import pytz
from scipy import signal

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import read_dia
import read_grid
import check_date

import cplot
import read_dia
import soundspeed
import fft_giops
import find_profile

import find_cspeed_maxmin

import tracemalloc

tracemalloc.start()
date=datetime.datetime(2022,6,1)
ddir='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
timeA, depthT, lone, late, ETFLD = read_dia.read_ensemble_plus_depthandtime(ddir, 'GIOPS_T', date, fld='T', time_fld='time_instant', file_pre='ORCA025-CMC-ANAL_1d_')
lone, late, ESFLD = read_dia.read_ensemble(ddir, 'GIOPS_T', date, fld='S', file_pre='ORCA025-CMC-ANAL_1d_')
timeT, depthT, lone, late, TTFLD = read_dia.read_ensemble_plus_depthandtime(ddir, 'GIOPS_T', date, fld='T', time_fld='time_instant', file_pre='ORCA025-CMC-TRIAL_1d_')
lone, late, TSFLD = read_dia.read_ensemble(ddir, 'GIOPS_T', date, fld='S', file_pre='ORCA025-CMC-TRIAL_1d_')

print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)


tim0=time.time(); MTFLD = find_cspeed_maxmin.add_mask(ETFLD, mask_var='tmask', mp=False); print(time.time()-tim0, np.stack(MTFLD).shape) 
tim0=time.time(); MTFLD = find_cspeed_maxmin.add_mask(ETFLD, mask_var='tmask', mp=True); print(time.time()-tim0, np.stack(MTFLD).shape) 
tim0=time.time(); MTFLD = find_cspeed_maxmin.add_mask(np.stack(ETFLD), mask_var='tmask'); print(time.time()-tim0, (MTFLD).shape) 


print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
snapshSot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno') 
print("[ Top 10 ]")
for stat in top_stats[:10]:
  print(stat)


tim0=time.time(); MTFLD = find_cspeed_maxmin.add_mask(TTFLD, mask_var='tmask', mp=False); print(time.time()-tim0, np.stack(MTFLD).shape) 
tim0=time.time(); MTFLD = find_cspeed_maxmin.add_mask(np.stack(TTFLD), mask_var='tmask'); print(time.time()-tim0, (MTFLD).shape) 

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno') 
print("[ Top 10 ]")
for stat in top_stats[:10]:
  print(stat)

lone, late, depthT, ETCFLD, ETFLD, ESFLD = find_cspeed_maxmin.read_cspeed_date(20220601, anal=False)
