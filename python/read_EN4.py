import sys
import numpy as np
#import matplotlib as mpl
#mpl.use('Agg')

import datetime
import pytz
import numbers

import netCDF4

utc=pytz.timezone('UTC')

file='/fs/site6/eccc/mrd/rpnenv/dpe000/EN4/EN.4.2.2.f.profiles.g10.202212.nc'
dirEN='/fs/site6/eccc/mrd/rpnenv/dpe000/EN4'
REFERENCE_DATE = datetime.datetime(1950,1,1,0,0,0,0, pytz.UTC)

def read_EN4_month(YY, MM, filepre='EN.4.2.2.f.profiles.g10'):
    year_str=str(YY).zfill(4)
    mont_str=str(MM).zfill(2)
    
    file = dirEN+'/'+filepre+'.'+year_str+mont_str+'.nc'
    LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_ENACT(file)
    return LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS

def read_EN4_months(YYS, MMS, filepre='EN.4.2.2.f.profiles.g10'):
    if ( isinstance(YYS, numbers.Number) ): YYS=[YYS]
    if ( isinstance(MMS, numbers.Number) ): MMS=[MMS]
    first=True
    for YY in YYS:
      for MM in MMS:
        ADD_LIST = read_EN4_month(YY, MM, filepre=filepre)
        if ( first ): 
            FUL_LIST = ADD_LIST
            first = not first
        else:
            FUL_LIST = extend_list_of_array(FUL_LIST, ADD_LIST)
    return FUL_LIST

def read_EN4_day(YY, MM, DD, filepre='EN.4.2.2.f.profiles.g10'):
     LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4_month(YY,MM, filepre=filepre) 
     date=datetime.datetime(YY,MM,DD,0,0,0,0,pytz.UTC)
     Iday = get_only_day(date, DAT, JUL)
     NAT=[DAT[iday] for iday in Iday]
     return LON[Iday], LAT[Iday], DEP[Iday,:], NAT, JUL[Iday], TW[Iday,:], SW[Iday,:], QT[Iday,:], QS[Iday,:]

def read_ENACT(file):
    dataset = netCDF4.Dataset(file) 
    TW=dataset.variables['POTM_CORRECTED'][:]
    SW=dataset.variables['PSAL_CORRECTED'][:]
    QT = ( dataset.variables['POTM_CORRECTED_QC'][:]== b'1' )
    QS = ( dataset.variables['PSAL_CORRECTED_QC'][:] == b'1' )
    DEP = dataset.variables['DEPH_CORRECTED'][:]
    JUL = dataset.variables['JULD'][:]
    LAT = dataset.variables['LATITUDE'][:]
    LON = dataset.variables['LONGITUDE'][:]
    
    DAT =  [ REFERENCE_DATE + datetime.timedelta(days=JULi) for JULi in JUL ]
    
    return LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS

def get_only_day(date, DAT, JUL):
    date=make_TZaware(date)
    days=( date - REFERENCE_DATE ).days + ( date - REFERENCE_DATE ).seconds/86400.
    Iday = np.where( ( JUL >= days ) & ( JUL < days+1 ) )
    Iday = Iday[0].tolist()
    
    Tday = [ ( DATi >= date ) and (DATi < date+datetime.timedelta(days=1) ) for DATi in DAT ]
    Jday = find_indices(Tday, True)
    if ( Iday == Jday ): return Iday
    print( Iday==Jday)
    return Iday    

def make_TZaware(date):
    if ( isinstance(date, list) ):
        new_date=[]
        for idate in date:
            new_idate = make_TZaware(idate)
            new_date.append(new_idate)
    elif ( isinstance(date, datetime.datetime) ):
        new_date = date.replace(tzinfo=pytz.UTC)
    else:
       new_date = []
    return new_date

def find_indices(list_to_check, item_to_find):
    return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]   

def find_both_valid_TS(QT, QS):
    IBTH = np.where( np.all((QT == QS),axis=1) )
    return IBTH[0]

def find_max_depth(QT, DEP):
    MAX_DEP = np.max(np.ma.array(DEP, mask=(1-QT)),axis=1)
    return MAX_DEP
    
def remove_minimum_depth( DEP, QT, min_depth=100.0):
   MAX_DEP = find_max_depth(QT, DEP)
   IDEEP =  np.where(MAX_DEP > min_depth) 
   return IDEEP[0]

def replace_list(ALIST, indices):
    NLIST = [ ALIST[ii] for ii in indices]
    return NLIST
    
def replace_array(ARRAY, indices, axis=0):
    if ( axis == 0 ):
        NARRAY = ARRAY[indices]
    else:
        NARRAY = np.transpose(np.transpose(ARRAY, [axis, 0])[indices], [axis, 0])
    return NARRAY
    
def replace_list_of_array(LIST, indices, axis=0):
    NEW_LIST = []
    for the_array in LIST:
        new_array=None
        if ( isinstance(the_array, np.ma.core.MaskedArray) or ( isinstance(the_array, np.ndarray) ) ):
            new_array= replace_array(the_array, indices, axis=axis)
        elif ( isinstance(the_array, list) ) : new_array=replace_list(the_array, indices)
        NEW_LIST.append(new_array)
    return NEW_LIST

def extend_list_of_array(LIST, EXTEND, axis=0):
    NEW_LIST = []
    for ilist in range(len(LIST)):
        if ( isinstance(LIST[ilist], list) ): NEW_LIST.append(LIST[ilist]+EXTEND[ilist])
        elif ( isinstance(LIST[ilist], np.ma.core.MaskedArray) or ( isinstance(LIST[ilist], np.ndarray) ) ):
            NEW_LIST.append(np.append(LIST[ilist], EXTEND[ilist], axis=0))
    return NEW_LIST
