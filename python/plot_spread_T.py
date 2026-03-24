
#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import datetime
import check_date

import plot_spread
import create_dates

expt='dev-4.0.0.ensembles_CTL'
leads = np.arange(24,169,24)
dates = create_dates.create_dates(20211013, 20220921,7)

glbvar, glbmne = plot_spread.cycle_thru_leads_date(expt, dates, leads, var='T', mp_loop=False)

