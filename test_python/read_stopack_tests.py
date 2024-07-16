import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')

import numpy as np
import datetime

import stfd
import cplot

expt='stopack_test4'
thedate=datetime.datetime(2022,5,4,0)

def get_halldir(hall=5, user='dpe000'):
    hallpre='/fs/site'+str(hall)+'/eccc/mrd/rpnenv/'+user+'/maestro/'
    return hallpre
    
def read_navs(file='/home/dpe000/data/ppp5/maestro/stopack_test4/hub/gridpt/prog/giops+1/2022050400_120'):
    nav_lon, nav_lat, __ = stfd.read_fstd_var(file, 'TM', typvar='P@')
    return nav_lon, nav_lat
    
def read_expt_SST(expt, date=datetime.datetime(2022,5,4, 0), lead=120, hall=5, ensemble=list(range(3))):
    if ( isinstance(ensemble, int) ): ensemble = list(range(ensemble))
    datestr=datestr=date.strftime("%Y%m%d%H")
    leadstr=str(lead).zfill(3)
    hallpre=get_halldir(hall)
    hallsuf=expt+'/hub/gridpt/prog/'
    eSST=[]
    for iens in ensemble:
        file=hallpre+hallsuf+'giops+'+str(iens)+'/'+datestr+'_'+leadstr
        #print(file)
        lev, FLD = stfd.read_fstd_multi_lev(file, 'TM', typvar='P@')
        SST=np.squeeze(FLD[np.where(np.array(lev) == 0 ) ])
        eSST.append(SST)
    return(eSST)

def find_stochastic_variation(expt, date=thedate, lead=120, hall=5):
    eSST=read_expt_SST(expt, date=date, lead=lead, hall=hall)      
    SST0, SST1, SST2 = eSST; SSTM = 0.5*(SST1+SST2)
    SSTstd1 = np.sqrt( 0.5 * ( np.square(SST1-SST0) + np.square(SST2-SST0) ) )
    SSTstd2 = np.sqrt( 0.5 * ( np.square(SST1-SSTM) + np.square(SST2-SSTM) ) )
    MSSTstd1 = np.mean(SSTstd1); MSSTstd2 = np.mean(SSTstd2)
    return MSSTstd1, MSSTstd2, SSTstd1, SSTstd2

def find_equivalence(expt1, expt2, date=thedate, lead=120, hall=5):
    eSST1=read_expt_SST(expt1, date=date, lead=lead, hall=hall) 
    eSST2=read_expt_SST(expt2, date=date, lead=lead, hall=hall) 
    ZEROS = []
    for iens, ensm in enumerate(eSST1):
        logiczero = np.all(eSST1[iens] == eSST2[iens])
        #print( logiczero )
        ZEROS.append(logiczero)
    return(ZEROS)
    
def find_mequivalence(expt, date=thedate, lead=120, hall=5):
    eSST=read_expt_SST(expt, date=date, lead=lead, hall=hall) 
    ZEROS = []
    for iens, ensm in enumerate(eSST):
      if ( iens != 0 ):
        logiczero = np.all(eSST[iens] == eSST[0])
        #print( logiczero )
        ZEROS.append(logiczero)
    return(ZEROS)

def do_tests():
    nav_lon, nav_lat = read_navs()
    print('Check ensemble std.')
    for expt in ['stopack_test4', 'stopack_test2', 'stopack_test1', 'stopack_cntl8', 'stopack_cntl7']: 
        MSSTstd1, MSSTstd2, SSTstd1, SSTstd2 = find_stochastic_variation(expt)
        print(expt, MSSTstd1, MSSTstd2)
        # produce plot
    rexpt = 'stopack_cntl7'
    print('Checking member equivalence of reference')
    print(rexpt, find_mequivalence(rexpt))
    print(' Checking Equivlence')
    for expt in ['stopack_test4', 'stopack_test2', 'stopack_test1', 'stopack_cntl7' ]:
        print(expt, find_equivalence(expt, rexpt))
        print(expt, find_mequivalence(expt))
