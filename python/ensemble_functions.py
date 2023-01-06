import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '/home/dpe000/python/properscoring-0.1')
import properscoring as ps

unique=['Lon', 'Lat']

def df_group_unique(df_in, vars, unique):
    df_group = df_in.groupby(unique, as_index='False')[vars]
    return df_group

def rm_sub_ensembles( df_in, vars, unique, ncount=21):
    if ( isinstance(df_in, list) ): 
        ncount = len(df_in)
        df_exec = pd.concat(df_in)
    else:
        df_exec = df_in.copy()
   
    df_group = df_group_unique(df_exec, vars+unique, unique)
    df_new = df_group.filter(lambda x:(x[vars[0]].count() == ncount) )

    return df_new

def rank(list):
    posn = [ ( value > 0 ) for value in list ]
    rank_val = sum(posn)
    return rank_val

def make_hist(rank, ncount):
    hist = np.zeros(ncount+1)
    hist[rank] = 1
    return hist

def dataframe_rank( df_in, var, unique, ncount=21):
    df_full = rm_sub_ensembles(df_in, [var], unique, ncount=ncount)
    df_group_full = df_group_unique(df_full, [var], unique)
    df_rank = df_group_full.apply(lambda x: rank(x.values.flatten())).rename('rank').reset_index()
    return df_rank

def dataframe_hist( df_rank, ncount=21 ):
    df_hist = df_rank['rank'].apply( lambda x: make_hist(x, ncount) ).rename('hist').reset_index()
    return df_hist

def dataframe_sum_hist(df_hist):
    df_sum_hist = np.sum(df_hist['hist'].values, axis=0)
    return df_sum_hist

def histo_array(df_rank, ncount=21):
    df_hist = dataframe_hist(df_rank, ncount=ncount)
    df_sum_hist = dataframe_sum_hist(df_hist)
    return df_sum_hist
    
def ens_mean( df_in, vars, unique, ncount=21):
    if ( isinstance(df_in, list) ): 
        ncount = len(df_in)
        df_exec = pd.concat(df_in)
    else:
        df_exec = df_in.copy()
        
    df_group = df_group_unique(df_exec, vars, unique)
    df_ensm = df_group.mean().reset_index()
    df_evar = df_group.var().reset_index()
    df_count = df_group.count().reset_index()
    LENGTH_LT = len(df_count[df_count[vars[0]] < ncount ])     
    LENGTH_GT = len(df_count[df_count[vars[0]] > ncount ])     
    if ( LENGTH_LT > 0 ):
        print('Number of SubEnsembles = ', LENGTH_LT, 'smallest', np.min(df_count[vars[0]]))    

    if ( LENGTH_GT > 0 ):
        print("WARNING:  Too many Ensemble Members")
        print(LENGTH_GT, np.max(df_count[vars[0]]))
        
    return df_ensm, df_evar

def calc_crps_df_err(df_in, unique, var='misfit'):
    if ( isinstance(df_in, list) ): 
        count = len(df_in)
        df_exec = pd.concat(df_in)
    else:
        df_exec = df_in.copy()

    df_group = df_group_unique(df_exec, [var], unique)
    df_crps = df_group.apply(lambda x: calc_crps(x.values.flatten(),0)).rename('crps').reset_index()
    return df_crps
    
def calc_crps_df_fld(df_in, unique, vars=['mod','obs']):
    if ( isinstance(df_in, list) ): 
        count = len(df_in)
        df_exec = pd.concat(df_in)
    else:
        df_exec = df_in.copy()

    df_exec = df_exec[vars+unique]
    #print(df_exec.keys(), df_in[0].keys())
    df_exec.rename( columns={ vars[0]:'fld', vars[1]:'obs'}, inplace=True)
    #print(df_exec.keys())
    df_group = df_group_unique(df_exec, ['fld', 'obs'], unique)
    print(df_group.mean().fld.values.shape, df_group.mean().obs.values.shape)
    df_crps = df_group.apply(lambda x: calc_crps(x.fld, x.obs.mean())).rename('crps').reset_index()
    return df_crps

def calc_crps(ens, obs):
    if ( isinstance(ens, np.ndarray) ):
        ens=ens.flatten()
    #print('shape', ens.shape, obs)
    crps = ps.crps_ensemble(obs, ens)
    return(crps)
