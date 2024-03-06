rcp = 3991.86795711963
rau0 = 1026.0
rau0_rcp =    rcp * rau0
KCONV=273.16

def Temperature_in_C(T):
    T_C = T - KCONV
    return T_C
    
def Temperature_in_K(T):
    T_K = T + KCONV
    return T_K
        
def heat_to_degC(H, depth=50, anomaly=False):
    TH = H / rau0_rcp / depth
    if (not anomaly):
        TH = Temperature_in_C(TH)
    return TH

def degC_to_heat(TC, depth=50, anomaly=False):
    if (not anomaly):
        TH = Temperature_in_K(TC)
    else:
        TH=TC
    H = TH * rau0_rcp * depth
    return H
