import os
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
from importlib import reload

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import time

import read_qcola
import create_dates
import cross_monitor

import create_ENMola

ddir = read_qcola.change_dir('+SAM2V2')

dates=create_dates.create_dates(20200101, 20200129, 7)
dates=create_dates.create_dates(20190925, 20191231, 7)
dates=create_dates.create_dates(20200205, 20200624, 7)
dates=create_dates.create_dates(20200603, 20200624, 7)
dates=create_dates.create_dates(20200415, 20200624, 7)
dates=create_dates.create_dates(20191009, 20200812, 7)
dates=create_dates.create_dates(20200701, 20200812, 7)

create_ENMola.calc_and_write_mean(dates, 'gx_EE1.0', ddir=ddir, trial='both', ensemble=list(range(1,21)))

create_ENMola.calc_and_write_mean(dates, 'gx_EE1.0', ddir=ddir, trial='trial', ensemble=list(range(1,21)))

create_ENMola.calc_and_write_mean(dates, 'gx_EE1.0', ddir=ddir, trial='iau', ensemble=list(range(1,21)))

create_ENMola.calc_and_write_mean(20200129, 'gx_EE1.0', ddir=ddir, trial='both', ensemble=list(range(1,21)))

