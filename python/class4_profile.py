time, depthT, lone, late, ETFLD_big = read_dia.read_ensemble_plus_depthandtime(find_cspeed_maxmin.mir5, 'GIOPS_T', datetime.datetime(2022,1,5), ensembles=range(21), time_fld='time_instant')
ENSEMBLES =  range(0, 21)
GIOPS_T 0 20220105
GIOPS_T 1 20220105
GIOPS_T 2 20220105
GIOPS_T 3 20220105
GIOPS_T 4 20220105
GIOPS_T 5 20220105
GIOPS_T 6 20220105
GIOPS_T 7 20220105
GIOPS_T 8 20220105
GIOPS_T 9 20220105
GIOPS_T 10 20220105
GIOPS_T 11 20220105
GIOPS_T 12 20220105
GIOPS_T 13 20220105
GIOPS_T 14 20220105
GIOPS_T 15 20220105
GIOPS_T 16 20220105
GIOPS_T 17 20220105
GIOPS_T 18 20220105
GIOPS_T 19 20220105
GIOPS_T 20 20220105
>>> LON, LAT, DEP, DAT, JUL, TW, SW, QT, QS = read_EN4.read_EN4_day(2022,1,4)>>> Tmod_list = []
>>> IJPTS = find_value_at_point.find_nearest_point_list(LON, LAT, lone, late)
>>> Tmod_list = []
>>> for ijpts in IJPTS:
...     ii, jj = ijpts
...     TENS = []
...     for TFLD in ETFLD_big:
...         TENS.append(TFLD[0, :, ii, jj])
...     Tmod_list.append(TENS)
... 
>>> T0 = TW[0]
>>> TMO0 = Tmod_list[0][0]
>>> dep0 = DEP[0]
>>> ivld = np.where(T0.mask == False)
>>> TWL = scipy.interpolate.griddata(dep0[ivld].data, T0[ivld].data, depthT.data)
>>> DT = TWL - TMO0
