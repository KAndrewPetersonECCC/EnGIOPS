import pandas as pd
import time
import sys
import os
import multiprocessing
import itertools
from functools import partial
import numpy as np

num_cpus = len(os.sched_getaffinity(0))
def find_common(DF_LIST):

    nens=len(DF_LIST)
    minobs=len(DF_LIST[0]) ; imin=0
    for iens in range(nens):
        if ( len(DF_LIST[iens]) < minobs ): 
            imin=iens
            minobs=len(DF_LIST[iens])
    #print(imin, minobs)

    DFM=DF_LIST[imin]    
    time0=time.time()
    NF_LIST=[]
    for iens, DF in enumerate(DF_LIST):
        #print(iens,time.time()-time0)
        #sys.stdout.flush()
        #NNF = pd.DataFrame()                    
        #NNF.empty
        NNF_list =[]
        for iobs in range(minobs):
           TMP_DF=DF.loc[ (DF['obs'] == DFM['obs'][iobs]) & (DF['Lat'] == DFM['Lat'][iobs]) & (DF['Lon'] == DFM['Lon'][iobs])] 
           NNF_list.append(TMP_DF)
        NNF = pd.concat(NNF_list)
        NNR = NNF.reset_index(drop=True)
        NF_LIST.append(NNR)
    return NF_LIST

def subset_DF(DF, key, value):
    DFS=DF.loc[ DF[key] == value ].reset_index()
    return DFS
    
def subset_list(DF_LIST, key, value):
   NF_LIST=[]
   for DF in DF_LIST:
       NF_LIST.append(subset_DF(DF,key, value))
   return NF_LIST

def resort_DFL_LIST(iens, DFL_LIST):
    NF=pd.concat( [NFL[iens] for NFL in DFL_LIST] )
    return NF

def find_common_in_Tstp(istp, DF_LIST):
    DFT_LIST=subset_list(DF_LIST, 'Tstp', istp)
    NFT_LIST=iterate_find_common(DFT_LIST)
    #print(istp, list_lengths(DF_LIST), list_lengths(DFT_LIST),  list_lengths(NFT_LIST) )
    return NFT_LIST

def find_common_by_Tstp(DF_LIST, mp=False, NTmax=1008):   # ANYTHING LESS THAN 1008 gives incomplete subset of DF_LIST
    if ( NTmax < 0 ): NTmax = max_value_in_list(DF_LIST, 'Tstp')
    nens=len(DF_LIST)
    time0=time.time()
    
    DFL_LIST = []
    for istp in range(1,NTmax+1):
        DFT_LIST = subset_list(DF_LIST, 'Tstp', istp)
        DFL_LIST.append(DFT_LIST)
    print( len(DFL_LIST) )  
    if ( mp ): 
        DFM_LIST=[]
        nproc=num_cpus
        for ii in  range(int(np.ceil(NTmax/nproc))):
            DFM_LIST.append(DFL_LIST[ii*nproc:(ii+1)*nproc])
        print( len(DFM_LIST) )   
    print('TSP', time.time() - time0)
    time0=time.time()
        
    if ( not mp ):
        NFL_LIST=[]
        for istp, DFT_LIST in enumerate(DFL_LIST):
            #NFT_LIST = find_common_in_Tstp(istp+1, DFT_LIST)  ## THIS REALLY ONLY NEED BE iterate_find_common !!
            #print(istp, time.time() - time0)
            NFT_LIST = iterate_find_common(DFT_LIST)
            NFL_LIST.append(NFT_LIST)
            print(istp, time.time() - time0)
    else:
        #pool = multiprocessing.Pool(num_cpus)
        NFL_LIST=[]
        for istp, DFN_LIST in enumerate(DFM_LIST):
            nproc=min([num_cpus, len(DFN_LIST)])
            pool = multiprocessing.Pool(nproc)
            NFN_LIST = pool.map(iterate_find_common, DFN_LIST)
            pool.close()
            pool.join()
            NFL_LIST.extend(NFN_LIST)
            print(istp, time.time() - time0, len(NFL_LIST))
        
    print('COM', time.time()-time0)
    time0=time.time()
    if ( ( not mp ) or ( True) ):
        NF_LIST=[]
        for iens in range(nens):
            NF=resort_DFL_LIST(iens, NFL_LIST)
            NF_LIST.append(NF)
    else:
        pool = multiprocessing.Pool(min([num_cpus, nens]),)
        izip= list(zip(range(nens), itertools.repeat(NFL_LIST)))
        #print(izip)
        NF_LIST = pool.starmap(resort_DFL_LIST, izip)
        pool.close()
        pool.join()
    print('FIN', time.time()-time0)
    return NF_LIST
    
def list_lengths(DF_LIST):
    LENGTH=[len(DF) for DF in DF_LIST]
    return LENGTH
    
def is_same_length(DF_LIST):
    LENGTH=[len(DF) for DF in DF_LIST]
    BINARY=[ LN==LENGTH[0] for LN in LENGTH]
    return all(BINARY)
    
def iterate_find_common(DF_LIST):
    NF_LIST = DF_LIST.copy()
    iteration = 0
    while ( not is_same_length(NF_LIST) ):
        NF_LIST = find_common(NF_LIST)
        iteration=iteration+1
        #print(iteration, is_same_length(NF_LIST), [len(NF) for DF in NF_LIST])
    return NF_LIST

def max_value_in_df(DF, key, fn=np.max):
    MAX = fn(DF[key].values)
    return MAX
    
def max_value_in_list(DF_LIST, key, mp=False, fn=np.max):
    nens=len(DF_LIST)
    nproc=min([nens, num_cpus])
    if ( mp ):
        epool = multiprocessing.Pool(nproc)
        izip = list(zip(DF_LIST, itertools.repeat(key)))
        MaxV = epool.starmap(partial(max_value_in_df, fn=fn), izip)
        epool.close()
        epool.join()
    else:
        MaxV=[]
        for DF in DF_LIST:
            MaxV.append(max_value_in_df(DF, key, fn=fn))
    return fn(np.array(MaxV))
