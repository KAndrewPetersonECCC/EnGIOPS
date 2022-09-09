#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import datetime
import numpy as np
import pickle

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import subprocess

import ola_functions
import cplot
import write_nc_grid
import find_common

test_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

def VP_dataframe(input_file):
    df_VP = ola_functions.VP_dataframe(input_file)
    return df_VP

