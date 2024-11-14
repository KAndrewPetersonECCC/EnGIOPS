
import struct
import os, sys, getopt
import numpy as np
import pandas as pd
from netCDF4 import num2date
import time
from collections import OrderedDict

# IS=InSitu ; VP=Vertical Profile (Argo) ; UV=Velocity? ; DS=SST (G6 analysis)
test_file='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T20/SAM2/20201230/DIA/2020123000_SAM.ola'

family = ['IS','VP','UV','DS']

def skip_header(f):
    """
    Function that skips the header and reads some needed information
    Input: Input file Identifier defined in main script
    Output: [Ndup, jpwork_array, TM, icycle] ..TO DEFINE LATER
    """
    for _ in range(20):
        header_length_bytes = f.read(4)
        nbytes = struct.unpack(">I", header_length_bytes)[0]
        f.seek(nbytes + 4, os.SEEK_CUR)
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print Len_bgn
    icycle  = struct.unpack(">I", f.read(4))[0] #;  print icycle
    TM      = struct.unpack(">3d", f.read(3 * 8)) #; print TM
    Len_end = struct.unpack(">I", f.read(4))[0] #; print Len_end
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: TM')
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print Len_bgn=
    Ndup    = struct.unpack(">4I", f.read(4 * 4)) #; print Ndup 
    jpwork_array = struct.unpack(">8I", f.read(8 * 4)) #; print jpwork_array
    jpwork_array = np.array(jpwork_array).reshape(4,2).transpose() #; print jpwork_array
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: Ndup')
    return [Ndup, jpwork_array, TM, icycle]


def read_var(f, var):
    print('Reading data for DUP_id = ', var)
    index = family.index(var.upper())
    for _ in range(index):
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
    # Real part
    if var.upper() == 'IS':
        print('We removed Hr in DUP_IS')
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        nblk = 12
        skip_Hr = 4 * (jpwork_array[0, index] - nblk)
        wk=[]
        for i in range(Ndup[index]):
            wk.extend(struct.unpack(">"+str(nblk)+"f", f.read(nblk * 4)))
            f.seek(skip_Hr, os.SEEK_CUR)
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], nblk).transpose()
    else:
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        if Len_bgn != 4 * Ndup[index]*jpwork_array[0,index]:
            sys.exit('records wrong::real, index = ' + str(index))
        wk = struct.unpack(">"+str(int(Len_bgn/4))+"f", f.read((int(Len_bgn/4)) * 4))
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], jpwork_array[0,index]).transpose()

    # Integer part
    Len_bgn = struct.unpack(">I", f.read(4))[0]
    if Len_bgn != 4 * Ndup[index] * jpwork_array[1, index]:
        sys.exit('records wrong::int,  index = ' + str(index))
    wk = struct.unpack(">"+str(int(Len_bgn/4))+"i", f.read((int(Len_bgn/4)) * 4))
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: float32')
    iga = np.array(wk).reshape(Ndup[index], jpwork_array[1,index]).transpose()
    return rga, iga

def read_data(source_file, var):
    global Ndup, jpwork_array, TM, icycle
    fid = open(source_file, 'rb')
    [Ndup, jpwork_array, TM, icycle] = skip_header(fid)
    rga, iga = read_var(fid, var)
    fid.close()
    return rga, iga

def weighted_average(df, data_col, weight_col, by_col):
    df['_data_times_weight'] = df[data_col]*df[weight_col]
    df['_weight_where_notnull'] = df[weight_col]*pd.notnull(df[data_col])
    g = df.groupby(by_col)
    result = g['_data_times_weight'].sum() / g['_weight_where_notnull'].sum()
    del df['_data_times_weight'], df['_weight_where_notnull']
    return result.get_values() 

def SFC_dataframe(input_file, var):
    print(input_file)
    # Read DS data
    rga_DS, iga_DS = read_data(input_file, var)

#        rga_DS = f.variables['rga_DS'][:]
#        iga_DS = f.variables['iga_DS'][:]

    # Extract variables and build dataframe

    lon = rga_DS[0, :]        # Longitude
    lat = rga_DS[1, :]        # Latitude
    tt  = rga_DS[2, :]        # Time (days since 1950-01-01 00:00:00)
    ov  = rga_DS[3, :]        # Observation value
    fv  = rga_DS[4, :]        # Model equivalent value
    av  = rga_DS[5, :]        # Analysis value (not used for now)
    dv  = rga_DS[6, :]        # Misfit value
    oe  = rga_DS[7, :]        # Observation error
    #
    duid  = iga_DS[0, :]      # Track number
    Tstp  = iga_DS[1, :]      # Model time step corresonding to observation time
    setid = iga_DS[8, :]      # Instrument indicator
    qc    = iga_DS[9, :]      # QC values (O: good obs;  1: bad obs)

    index = range(len(lon))
    df_DS        = pd.DataFrame(lon, index=index, columns=['Lon'])
    df_DS['Lat'] = pd.DataFrame(lat, index=index)
    df_DS['tt']  = pd.DataFrame(tt,  index=index)
    df_DS['obs']  = pd.DataFrame(ov,  index=index)
    df_DS['mod']  = pd.DataFrame(fv,  index=index)
    df_DS['ana']  = pd.DataFrame(av,  index=index)
    df_DS['misfit']  = pd.DataFrame(dv,  index=index)
    df_DS['setID']  = pd.DataFrame(setid,  index=index)
    df_DS['oerr']  = pd.DataFrame(oe,  index=index)
    df_DS['TrackNum']  = pd.DataFrame(duid,  index=index)
    df_DS['Tstp']  = pd.DataFrame(Tstp,  index=index)
    df_DS['QC']  = pd.DataFrame(qc,  index=index)

#    # Convert tt to date
    tmp = num2date(tt, "days since 1950-01-01 00:00:00") 
    df_DS['obsdate'] = pd.DataFrame(tmp, index=index)

    print('Accepted data number: ', len(df_DS))
    print('Rejected data number: ', len(df_DS[df_DS['QC'] == 1]))

    # Concatenate dataframes and remove rejected obs
    df_DS = subset_df(df_DS, 'QC', 0 )

    return df_DS

def SST_dataframe(input_file):
    df_DS = SFC_dataframe(input_file, 'DS')
    
    # Extract SST
    df_DS_SST = subset_df(df_DS, 'setID', 40)
    
    # Extract SST_NIGHT
    df_DS_SST_NIGHT = subset_df(df_DS, 'setID', 41)

    return df_DS_SST, df_DS_SST_NIGHT, df_DS

def SST_DAY_dataframe(input_file, NIGHT=True):
    df_DS = SFC_dataframe(input_file, 'DS')
    if ( not isinstance(NIGHT, type(None)) ):
        if ( NIGHT ):
	        df_DS = subset_df(df_DS, 'setID', 41)
        else:   
	        df_DS = subset_df(df_DS, 'setID', 40)
    return df_DS   
	
def SSH_dataframe(input_file):
    df_IS = SFC_dataframe(input_file, 'IS')
    # Extract data by obs category
    df_IS_AL   = df_IS[df_IS['setID'] == 13]
    df_IS_C2   = df_IS[df_IS['setID'] == 11]
    df_IS_J2   = df_IS[df_IS['setID'] ==  3]
    df_IS_J3   = df_IS[df_IS['setID'] == 15]
    df_IS_J2N  = df_IS[df_IS['setID'] == 16]
    df_IS_H2   = df_IS[df_IS['setID'] == 14]
    df_IS_S3A  = df_IS[df_IS['setID'] == 17]
    return df_IS_AL, df_IS_C2, df_IS_J2, df_IS_J3, df_IS_J2N, df_IS_H2, df_IS_S3A, df_IS

def subset_SSH_dataframe(df_IS, SAT='ALL'):
    if ( ( SAT == 'ALL' ) or ( SAT == 'NONE' ) ): 
        df_subset = df_IS
    elif ( ( SAT == 'ALTIKA' ) or ( SAT == 'AL' ) or ( SAT == '13' ) ):
        df_subset = df_IS[df_IS['setID'] == 13]
    elif ( ( SAT == 'CRYOSAT2' ) or ( SAT == 'C2' ) or ( SAT == '11' ) ):
        df_subset = df_IS[df_IS['setID'] == 11]
    elif ( ( SAT == 'JASON2' ) or ( SAT == 'J2' ) or ( SAT == '3' ) ):
        df_subset = df_IS[df_IS['setID'] == 3]
    elif ( ( SAT == 'JASON3' ) or ( SAT == 'J3' ) or ( SAT == '15' ) ):
        df_subset = df_IS[df_IS['setID'] == 15]
    elif ( ( SAT == 'JASON2N' ) or ( SAT == 'J2N' ) or ( SAT == '16' ) ):
        df_subset = df_IS[df_IS['setID'] == 16]
    elif ( ( SAT == 'HY2A' ) or ( SAT == 'H2' ) or ( SAT == '14' ) ):
        df_subset = df_IS[df_IS['setID'] == 14]
    elif ( ( SAT == 'SENTINEL3A' ) or ( SAT == 'SENTINEL') or ( SAT == 'S3A' ) or ( SAT == '17' ) ):
        df_subset = df_IS[df_IS['setID'] == 17]
    else:
        df_subset = df_IS
    return df_subset

def SSH_SAT_dataframe(input_file, SAT='ALL'):
    df_IS = SFC_dataframe(input_file, 'IS')
    df_subset = subset_SSH_dataframe(df_IS, SAT=SAT)
    return df_subset

def subset_df(df, key_id, val):
    if ( not key_id in df.keys() ):
        df_sub = pd.DataFrame()
        df_sub.empty
    elif ( len(df[df[key_id] == val ]) == 0 ):
        df_sub = pd.DataFrame()
        df_sub.empty
    else:
        df_sub = df[df[key_id] == val ]
    return df_sub
   
def VP_dataframe(input_file):

    # Model levels depths
    depth = np.loadtxt('/home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_depths')
    nlevels=int(len(depth))
    depth = np.concatenate((depth[:], depth[:]))
    maxMVS = int((nlevels-1)*2)   # Maximum levels number
    ip_jkdta_TEM = 2     # the first index for SST, only for present and before GIOPS300b
    ip_jkdta_TEM = 1

    rga_VP, iga_VP = read_data(input_file, 'VP')
    nv, nprf = rga_VP.shape
    ni, npri = iga_VP.shape

    df_g = pd.DataFrame(np.nan, index=[], columns=[])

    if ( nprf != npri ):
        print('Inconsistent number profiles: nprf/npri', nprf, npri)
        return df_g
        
    if (nv != maxMVS*5+7):  
        print('Wrong dimension: nv in rga_VP', nv, maxMVS)
        #return df_g
    
    #if (ni != maxMVS*2+10):   # for GIOPSv2
    if (ni != maxMVS*2+11):   # for GIOPSv3
        print('Wrong dimension: ni in iga_VP', ni, maxMVS)
        #return df_g

    #Initialization
    df_g = pd.DataFrame(np.nan, index=[], columns=[])
    vo = np.empty((2*nlevels, nprf)) * np.nan
    vf = np.empty((2*nlevels, nprf)) * np.nan
    vg = np.empty((2*nlevels, nprf)) * np.nan
    dv = np.empty((2*nlevels, nprf)) * np.nan
    dep = np.empty((2*nlevels, nprf)) * np.nan
    start = time.time()
    df_list = []
    
    for pr in range(nprf):
        nmvs = iga_VP[9, pr]
        idx = np.arange(nmvs)
        kk = iga_VP[idx+10, pr] - ip_jkdta_TEM
        if int(kk.max()) >= 2*nlevels:
            print("problem with profile: {0}".format(pr))
            print("kk.max(), maxMVS", kk.max(), maxMVS, pr)
            continue
        if int(kk.min()) < 0:
            print("problem with profile: {0}".format(pr))
            print("kk.max(), maxMVS", kk.max(), maxMVS, pr)
            continue
        kk = kk[iga_VP[idx+10+maxMVS, pr] == 0].tolist()
        #print('kk', kk)
        #if ( min(kk) <= 1 or max(kk) > 97 ):
        #  print('kk', min(kk), max(kk), pr)
        vo[kk, pr] = rga_VP[idx+3, pr]
        vf[kk, pr] = rga_VP[idx+3+maxMVS*1, pr]
        vg[kk, pr] = rga_VP[idx+3+maxMVS*2, pr]   # What is this?  VALUE FROM ANALYSIS.  NOT USED
        dv[kk, pr] = rga_VP[idx+3+maxMVS*3, pr]
        dep[kk, pr] = depth[kk]
        vo_T = vo[:nlevels, pr]
        vo_S = vo[nlevels:, pr]
        vf_T = vf[:nlevels, pr]
        vf_S = vf[nlevels:, pr]
        dv_T = dv[:nlevels, pr]
        dv_S = dv[nlevels:, pr]
        nT=len(np.where(np.isfinite(vo_T))[0])
        nS=len(np.where(np.isfinite(vo_S))[0])
        lon = np.repeat(np.array(rga_VP[0, pr]), nlevels)
        lat = np.repeat(np.array(rga_VP[1, pr]), nlevels)
        date = np.repeat(np.array(rga_VP[2, pr]), nlevels) 
        setID = np.repeat(np.array(iga_VP[8, pr]), nlevels)
        depth_T = dep[:nlevels, pr]
        depth_S = dep[nlevels:, pr]
        dic = OrderedDict([('lon', lon),
                           ('lat', lat),
                           ('depth_T', depth_T),
                           ('depth_S', depth_S),  
                           ('date', date),
                           ('voT', vo_T),
                           ('voS', vo_S),
                           ('vfT', vf_T),
                           ('vfS', vf_S),
                           ('misfitT', dv_T),
                           ('misfitS', dv_S),
                           ('setID', setID)])
        df = pd.DataFrame.from_dict(dic)
        del dic
        df_list.append(df)
    npri=len(df_list)
    print("Found : {0}/{1} profiles   Treated in {2} s".format(nprf, npri, time.time()-start)  )  
    
    df_g = pd.concat(df_list, axis=0, ignore_index=True, copy=False)
    return df_g
    
