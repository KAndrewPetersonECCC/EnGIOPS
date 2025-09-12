import numpy as np

def zero_levs(IM, II):
    IMAX = np.abs(IM)
    IMIN = -1.0 * IMAX
    II = np.abs(II)
    ticks = np.arange( IMIN, IMAX+II, 2*II)
    leves = np.arange( IMIN+II/2, IMAX, II)
    return leves, ticks
    
