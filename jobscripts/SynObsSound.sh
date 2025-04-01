#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/SynObsSound.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/SynObsSound.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

BJOB=/home/dpe000/EnGIOPS/JOBS/SO_sound.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/SO_sound.py
OJOB=/home/dpe000/EnGIOPS/python/find_cspeed_tmp.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python3 ${PJOB}
EOB


cat > ${PJOB} << EOP
#from importlib import reload
import sys
import os
import datetime
import numpy as np

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin
import more_cspeed

start=[2020,1]
final=[2020,12]

print("RESULTS for INST:  CNTL, NoArgo, NoAlt -- smaller better")
BRSC_slist = []
for inst in ['FOAM', 'MOVE-G3', 'GIOPS', 'JCOPE_FGO01']:
    BRSC_list= []
    ddir=more_cspeed.ddirS
    expts = ['CNTL', 'NoArgo', 'NoAlt']
    if ( inst == 'GIOPS' ): ddir=more_cspeed.odird
    #if ( inst == 'JCOPE_FGO01' ): expts = ['CNTL']
    for expt in expts:
        BRSC, MISS, ALARM =more_cspeed.do_cspeed_expt(inst, expt, start, final, ref="Ref", ddir=ddir, odir=more_cspeed.odird)
        BRSC_list.append(BRSC)
    print(inst, BRSC_list)
    BRSC_ref = BRSC_list[0]
    print("DIFF", [BRSC - BRSC_ref for BRSC in BRSC_list])
    BRSC_slist.append(BRSC_list)


#FOAM [0.11815689395949412, 0.11798001238171045, 0.11845169658913357]
#DIFF [0.0, -0.00017688157778367186, 0.0002948026296394485]
#MOVE-G3 [0.10067509802187435, 0.11010878217033696, 0.09982017039591994]
#DIFF [0.0, 0.009433684148462601, -0.0008549276259544186]
#GIOPS [0.10559830193685328, 0.11836325580024173, 0.10671855192948321]
#DIFF [0.0, 0.012764953863388454, 0.0011202499926299264]

## EN4 results
## CNTL, NoArgo, NoAlt
## 0.1398,  0.1574, 0.1439
## 0.0, 0.0176, 0.0041]                                                                                                                                                               

expts=['CNTL', 'NoArgo', 'NoAlt', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'SSTonly', 'Free']
refs=['Ref', 'Asm']
inst='GIOPS'
ddir=more_cspeed.odird
start=[2020,1]
final=[2022,12]

for expt in expts:
    for ref in refs:
        BRSC, MISS, ALARM = more_cspeed.do_cspeed_expt(inst, expt, start, final, ref=ref, ddir=ddir, odir=more_cspeed.odird)
        print(ref, expt, BRSC, MISS, ALARM)
        
                    
EOP

${SJOB}
