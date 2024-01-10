#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/test_BRSC.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/test_BRSC.sh

cd /home/dpe000/EnGIOPS/
source jobscripts/prepython.sh 

python << EOD

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import datetime
import pytz
import time

import find_cspeed_maxmin

YEARS=[2020, 2021]
EXD = (datetime.datetime(2020, 10, 9, 0,0,0,0, pytz.UTC) , datetime.datetime(2021, 10, 12, 0,0,0,0, pytz.UTC))
hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

find_cspeed_maxmin.calc_class4_duct_cycle(datetime.datetime(2022,6,1))
for idate, date in enumerate(EXD):

    [BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL],[SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL]  = find_cspeed_maxmin.calc_class4_duct(date, ddir=mir5)
    print('Brier Scores', BRSC, BRAN, BRM1, BRS1, BRGD, BRLG, BRCL)
    print('Spread Values', SPRD, SPAN, SPM1, SPS1, SPGD, SPLG, SPCL)

EOD
