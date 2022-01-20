#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/loop_dates.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/loop_dates.sh


TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS

command=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh
date_start=20190313
date_final=20201230

export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto

python << EOD
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime

import subprocess
import datadatefile

dateint=${date_start}
date=datadatefile.convert_strint_date(dateint)
datee=datadatefile.convert_strint_date(${date_final})

while ( date <= datee ):
    datestr, dateint=datadatefile.convert_date_strint(date)
    subprocess.call(['bash', '${command}', '-d='+datestr])
    date=date+datetime.timedelta(days=7)
    
EOD
