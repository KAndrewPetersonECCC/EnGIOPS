import numpy as np
from scipy.spatial import cKDTree

def grid(delta=2.0, box=[-180, 180, -90, 90] ):
    XW=box[0]
    XE=box[1]
    YS=box[2]
    YN=box[3]
    # Define lats and lons for 2x2 bins
    bins_lons = np.arange(XW+delta/2.0, XE, delta)  
    bins_lats = np.arange(YS+delta/2.0, YN, delta)
    xlon = bins_lons
    xlon.shape = bins_lons.shape + (1,)
    xlat = bins_lats
    xlat.shape = bins_lats.shape + (1,)
    query_lon = cKDTree(xlon)
    query_lat = cKDTree(xlat)
    return bins_lons, bins_lats, xlon, xlat, query_lon, query_lat

def nearest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before

def nearest2(myList, myNumbers):
    myList = np.array(myList)
    myNumbers = np.array(myNumbers) 
    myList.shape = myList.shape + (1,)
    myNumbers.shape = myNumbers.shape + (1,)
    t = KDTree(myList)
    dists, inds = t.query(myNumbers)
    return myList[inds]  


def nearest3(tree, myList, myNumbers):
    '''
    Group to the nearest values given in myList
    inputs:
    tree: preprocessed myNumbers date using cKDTree tool 
    myList: list used to group data
    myNumber: original data 
    '''
    x = myNumbers
    x.shape = x.shape + (1,)
    dists, inds = tree.query(x)
    return myList[inds]
