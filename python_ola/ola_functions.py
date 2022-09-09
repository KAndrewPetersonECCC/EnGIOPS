
import struct
import os, sys, getopt
import numpy as np



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
    Len_bgn = struct.unpack(">I", f.read(4))[0] #; print Len_bgn
    Ndup    = struct.unpack(">4I", f.read(4 * 4)) #; print Ndup 
    jpwork_array = struct.unpack(">8I", f.read(8 * 4)) #; print jpwork_array
    jpwork_array = np.array(jpwork_array).reshape(4,2).transpose() #; print jpwork_array
    Len_end = struct.unpack(">I", f.read(4))[0]
    if (Len_end != Len_bgn):
        sys.exit(' records wrong:: Ndup')
    return [Ndup, jpwork_array, TM, icycle]


def read_var(f, var):
    print 'Reading data for DUP_id = ', var
    index = family.index(var.upper())
    for _ in range(index):
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
        Len_bgn = struct.unpack(">I", f.read(4))[0]
        f.seek(Len_bgn + 4, os.SEEK_CUR)
    # Real part
    if var.upper() == 'IS':
        print 'We removed Hr in DUP_IS'
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
        wk = struct.unpack(">"+str(Len_bgn/4)+"f", f.read((Len_bgn/4) * 4))
        Len_end = struct.unpack(">I", f.read(4))[0]
        if (Len_end != Len_bgn):
            sys.exit(' records wrong:: float32')
        rga = np.array(wk).reshape(Ndup[index], jpwork_array[0,index]).transpose()
	
    # Integer part
    Len_bgn = struct.unpack(">I", f.read(4))[0]
    if Len_bgn != 4 * Ndup[index] * jpwork_array[1, index]:
        sys.exit('records wrong::int,  index = ' + str(index))
    wk = struct.unpack(">"+str(Len_bgn/4)+"i", f.read((Len_bgn/4) * 4))
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


