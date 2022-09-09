
import struct
import os, sys, getopt
import numpy as np
import pandas as pd
from netCDF4 import num2date

# IS=InSitu ; VP=Vertical Profile (Argo) ; UV=Velocity? ; DS=SST (G6 analysis)

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
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print(Len_bgn)
    icycle  = struct.unpack(">I", f.read(4))[0] #;  print(icycle)
    TM      = struct.unpack(">3d", f.read(3 * 8)) #; print(TM)
    Len_end = struct.unpack(">I", f.read(4))[0] #; print(Len_end)
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: TM')
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print(Len_bgn)
    Ndup    = struct.unpack(">4I", f.read(4 * 4)) #; print(Ndup) 
    jpwork_array = struct.unpack(">8I", f.read(8 * 4)) #; print(jpwork_array)
    jpwork_array = np.array(jpwork_array).reshape(4,2).transpose() #; print(jpwork_array)
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
            wk.extend(struct.unpack(">"+str(nblk)+"f", f.read(int(nblk * 4))))
            f.seek(skip_Hr, os.SEEK_CUR)
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], nblk).transpose()
    else:
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        if Len_bgn != 4 * Ndup[index]*jpwork_array[0,index]:
            sys.exit('records wrong::real, index = ' + str(index))
        wk = struct.unpack(">"+str(int(Len_bgn/4))+"f", f.read(int(Len_bgn/4) * 4))
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


    # Extract SST
    df_DS_SST = subset_df(df_DS, 'setID', 40)
    
    # Extract SST_NIGHT
    df_DS_SST_NIGHT = subset_df(df_DS, 'setID', 41)

    return df_DS_SST, df_DS_SST_NIGHT, df_DS

def SST_dataframe(input_file):
    df_DS = SFC_dataframe(input_file, 'DS')
    
    # Extract SST
    df_DS_SST = subset_df(df_DS, 'setID', 40)
    
    # Extract SST_NIGHT
    df_DS_SST_NIGHT = subset_df(df_DS, 'setID', 41)

    return df_DS_SST, df_DS_SST_NIGHT, df_DS
    
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
   
