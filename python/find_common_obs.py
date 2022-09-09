import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import datetime
import numpy as np

import multiprocessing
import itertools

def match_obs(OBS, DF_list):   
    MATCH_INDEX = []
    nlis = len(DF_list)
    for ilis in range(nlis):
        imatch=np.where( ( DF_list[ilis]['Lon'] == OBS['Lon'] ) 
                       & ( DF_list[ilis]['Lat'] == OBS['Lat'] ) 
                       & ( DF_list[ilis]['obs'] == OBS['obs'] )
                       & ( DF_list[ilis]['TrackNum'] == OBS['TrackNum'] ) 
                          )
        if ( len(imatch[0]) == 0 ):
            MATCH_INDEX.append(-1)
        else:
            MATCH_INDEX.append( imatch[0][0] )
    return MATCH_INDEX
   
def common_obs_set(DF_list, MATCH_INDEX):
    UPOBS_LIST = []
    for ilis, match_index in enumerate(MATCH_INDEX):
        UPOBS_LIST.append(DF_list[ilis].loc[match_index])
    return UPOBS_LIST

def process_common_obs(iobs, df_base, DF_list, DF_newl, nomatch_list):
    OBS = df_base.loc[iobs]    
    nlis = len(DF_list)
    MATCH_LIST = match_obs(OBS, DF_list)
    if ( -1 in MATCH_LIST ):
        nomatch_list.append(iobs)
    else:
        UPOBS_LIST = common_obs_set(DF_list, MATCH_LIST)
        for ilis in range(nlis):
            DF_newl[ilis].loc[iobs] = UPOBS_LIST[ilis]
    return
    
def drop_no_match(DF_newl, no_match):
    DF_finl=[]
    nlis = len(DF_newl)
    for ilis in range(nlis):
        DF_finl.append( DF_newl[ilis].drop([DF_newl[ilis].index[iindex] for iindex in no_match ]) )
    for ilis in range(nlis):
        print(len(DF_finl[ilis]))
    return DF_finl
             
def find_common_IS(DF_list, nproc):
    nlis=len(DF_list)
    NO_list = [ len(df) for df in DF_list ]
    nobs = min(NO_list) 
    df_base = DF_list[NO_list.index(nobs)].copy()
    
    DF_newl = []
    for ilis in range(nlis):
        DF_newl.append(df_base.copy())

    time0 = time.time()
    nomatch_list = []        
    pool = multiprocessing.Pool(nproc)
    #pool = multiprocessing.Pool()
    # in python 2.7 <-> itertools.izip <-> zip 
    #zip = itertools.izip(range(nobs), itertools.repeat(df_base), itertools.repeat(DF_list), itertools.repeat(DF_newl), nomatch_list)
    zip = zip(range(nobs), itertools.repeat(df_base), itertools.repeat(DF_list), itertools.repeat(DF_newl), nomatch_list)
    #pool.map(process_common_obs_iobs, range(nobs) )
    pool.map(process_common_obs, zip)
    #for iobs in range(nobs): 
    #    if ( iobs%10000 == 0 ): 
    #       print(iobs, time.time() - time0)
    #       sys.stdout.flush()
    #    process_common_obs_iobs(iobs)
    print(nomatch_list)
    DF_finl = drop_no_match(DF_newl, no_match)
    return

