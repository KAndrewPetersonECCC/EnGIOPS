import numpy as np
import numbers

def Kelvin_to_Celsius(T, reverse=False):
    TKC = 273.15
    if ( not reverse ):
        TC = ( T - TKC )
    elif ( reverse ):
        TC = ( T+ TKC )  # Actually Temperature in Kelvin
    return TC
    
def sound_speed(D, S, T, source="Mackenzie"):
    """
    source = Mackenzie (1981) (default)
           = Coppens (1981)
           = Unesco (1995) [Depth is actually Pressure in bars]
    """

    if ( isinstance(T, list) ): T = np.array(T)
    if ( isinstance(S, list) ): S = np.array(S)
    if ( isinstance(D, list) ): D = np.array(D)
    
    # All temperatures are in Celsius; If not realistic convert"
    
    if ( isinstance(T, numbers.Number) ):
      if ( T > 200.0 ):
        print("Converting Temperature to Celsius.  Please do this before passing.")
        T = Kelvin_to_Celsius(T)
    else:
        if ( isinstance(T, np.ma.core.MaskedArray) ):
            iconv = np.ma.where(T>200)
        elif ( isinstance(T, np.ndarray) ):
            iconv = np.where(T>200)
        if ( len(iconv[0]) > 0 ):
            print("Converting Temperature to Celsius.  Please do this before passing.")
            print(T[iconv])
        T[iconv] = Kelvin_to_Celsius(T[iconv])
        if ( len(iconv[0]) > 0 ):
            print(T[iconv])
    if ( source == 'Mackenzie' or source == 'M' ):
        cspeed = sound_speed_Mackenzie(D, S, T)
    elif ( source == 'Coppens' or source == 'C' ):
        cspeed = sound_speed_Coppens(D, S, T)
    elif ( source == 'UNESCO' or source == 'UN' ):
        cspeed = sound_speed_UNESCO(T, S, D) # NOTE D is actually Pressure in Bar"
    return cspeed
    
def sound_speed_Mackenzie(D, S, T):
    """
    c = sound speed in metres (returned)
    T = temperature in degrees Celsius
    S = salinity in parts per thousand
    D = depth in metres
    """
    c = ( 
          1448.96 + 4.591*T - 5.304e-2 * T**2 + 2.374e-4 * T**3 
        + 1.340 * (S - 35.0) + 1.630E-2 * D + 1.675e-7 * D**2 
        - 1.025e-2 * T * (S-35.0) - 7.139e-13 * T * D**3
        )
    return c
    
def sound_speed_Coppens(D, S, T):
    smallT = T/10.0
    Dkm = D/1000.
    c0 = (
           1449.05 + 45.7*smallT - 5.21*smallT**2 + 0.23*smallT**3
         + ( 1.333 - 0.126*smallT + 0.009*smallT**2 )*(S-35.0)
         )
         
    c = c0 + ( 16.23 + 0.253*smallT )*Dkm+ ( 0.016 + 0.0002*(S-35.0) )*(S-35)*smallT*Dkm
    return c
