#!/bin/bash -x
#bash /home/dpe000/EnGIOPS/jobscripts/date_BRSC.sh -d=CCYYMMDD

USAGE="date_BRSC.sh -d=CCYYMMDD"

## GET arguments
SynObs=False
SynObs2=False
SynObsE2=False
KeyList="['CNTL', 'Free', 'NoArgo', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'Oper', 'SSTonly', 'NoAlt']"
KeyList2="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV2', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV2', 'NoAltV2']"
KeyList3="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']"
OutDir=None
InDir=None
ExpList=None
EnsList="'-d'"
AnlList=False

#dlist=['/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle', '/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle']
#keylist=['IC4','CTL','IC4_l', 'CTL_l']
#explist=['GX35FCH22V2', 'IC4GX340EH22-CTR','GX35FCH22V2', 'IC4GX340EH22-CTR']
#enslist=['d','d','l','l']

for i in "$@"
do
case $i in
    -d=*|--date=*)
    DATE="${i#*=}"
    shift # past argument=value
    ;;
    -s|--SO|--SynObs)
    SynObs=True
    shift # past argument=value
    ;;
    --SO2|--SynObs2)
    SynObs2=True
    shift # past argument=value
    ;;
    --SOE2|--SynObsE2)
    SynObsE2=True
    shift # past argument=value
    ;;
    --SO3|--SynObs3)
    SynObs3=True
    shift # past argument=value
    ;;
    --SOE3|--SynObsE3)
    SynObsE3=True
    shift # past argument=value
    ;;
    -o=*|--outdir=*)
    OutDir="${i#*=}"
    shift # past argument=value
    ;;
    -i=*|--indir=*)
    InDir="${i#*=}"
    shift # past argument=value
    ;;
    -k=*|--keylist=*)
    KeyList="${i#*=}"
    shift # past argument=value
    ;;
esac
done
if [[ -z ${DATE} ]]; then
   echo "DATE required"
   echo ${USAGE}
   exit 99
fi
if [[ ${#DATE} -lt 8 ]] ; then
   echo "DATE CCYYMMDD required"
   echo $USAGE
   exit 99
fi

if [[ ${SynObs} == True ]] ; then 
    if [[ ${InDir} == None ]] ; then 
        InDir=SynObs
    fi
fi
if [[ ${SynObs2} == True ]] ; then 
    if [[ ${InDir} == None ]] ; then 
        InDir=SynObs2
    fi
fi
if [[ ${SynObsE2} == True ]] ; then 
    if [[ ${InDir} == None ]] ; then 
        InDir=SynObsE2
    fi
fi
if [[ ${SynObs3} == True ]] ; then 
    if [[ ${InDir} == None ]] ; then 
        InDir=SynObs3
    fi
fi
if [[ ${SynObsE3} == True ]] ; then 
    if [[ ${InDir} == None ]] ; then 
        InDir=SynObsE3
    fi
fi

if [[ ${OutDir} == None ]] ; then
    if [[ ${SynObs} == False ]] ; then
        OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/CLASS4'"
    fi
fi

APPD=''
if [[ ${InDir} == SynObs ]] ; then
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBS1'"
    InDir="'/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs'"
    KeyList="['CNTL', 'Free', 'NoArgo', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'Oper', 'SSTonly', 'NoAlt']"
    ExpList="${KeyList}"
    EnsList="'d'"
    AnlList=False
fi
if [[ ${InDir} == SynObs2 ]] ; then
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBS2'"
    InDir="'/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs'"
    KeyList="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV2', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV2', 'NoAltV2']"
    ExpList="${KeyList}"
    EnsList="'d'"
    AnlList=False
fi
if [[ ${InDir} == SynObsE2 ]] ; then
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBSE2'"
    InDir="'/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs'"
    KeyList="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV2', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV2', 'NoAltV2']"
    ExpList="${KeyList}"
    EnsList="'l'"
    AnlList=False
fi
if [[ ${InDir} == SynObs3 ]] ; then
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBS3'"
    InDir="'/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs'"
    KeyList="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']"
    ExpList="${KeyList}"
    EnsList="'d'"
    AnlList=False
fi
if [[ ${InDir} == SynObsE3 ]] ; then
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/SYNOBSE3'"
    InDir="'/home/saqu500/data_maestro/ppp5/maestro_archives/SynObs'"
    KeyList="['CNTLV2', 'Free', 'NoArgoV2', 'HalfArgoV2', 'NoInsituV3', 'NoMoorV2', 'NoSSTV2', 'Oper', 'SSTonlyV3', 'NoAltV2']"
    ExpList="${KeyList}"
    EnsList="'l'"
    AnlList=False
fi
if [[ ${InDir} == IC4_A ]] ; then
    APPD=".A"
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/IC4_A'"
    InDir="['/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle']"
    KeyList="['IC4','CTL']"
    ExpList="['GX35FCH22V2', 'IC4GX340EH22-CTR']"
    EnsList="['d','d']"
    AnlList=False
fi
if [[ ${InDir} == IC4_B ]] ; then 
    APPD=".B"
    SynObs=True
    OutDir="'/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/CSPEED/IC4_B'"
    InDir="['/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle', '/home/sprj700/data_maestro/ppp6/maestro_archives', '/home/kch001/data_maestro/ppp6/maestro_archives/IC4_final_cycles/controle']"
    KeyList="['IC4','CTL','IC4_l', 'CTL_l']"
    ExpList="['GX35FCH22V2', 'IC4GX340EH22-CTR','GX35FCH22V2', 'IC4GX340EH22-CTR']"
    EnsList="['d','d','l','l']"
    AnlList=False
fi
echo "KEYLIST ${KeyList}"

DATE=${DATE:0:8}

cd /home/dpe000/EnGIOPS/

BJOB=/home/dpe000/EnGIOPS/JOBS/BRSC_${DATE}.${SynObs}${APPD}.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/BRSC_${DATE}.${SynObs}${APPD}.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB
cd  /home/dpe000/EnGIOPS/
source jobscripts/prepython.sh
python ${PJOB}
EOB

cat > ${PJOB} << EOP

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import time
import datetime
import check_date
import find_cspeed_maxmin

hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

date = check_date.check_date(${DATE}, outtype=datetime.datetime)
print(date)
if ( ${SynObs} ):
    print(${SynObs})
    keylist=${KeyList}
    explist=${ExpList}
    enslist=${EnsList}
    anllist=${AnlList}
    dirlist=${InDir}
    print('KEYLIST', keylist)
    find_cspeed_maxmin.calc_class4_duct_SYNOBS_cycle(date, keylist=keylist, odir=${OutDir}, dirlist=dirlist, explist=explist, enslist=enslist, anllist=anllist)
else:
    print('Class4')
    find_cspeed_maxmin.calc_class4_duct_cycle(date)

EOP

echo ${SJOB}
${SJOB}
