import matplotlib.pyplot as plt
def_plots=[ [['T',0,'SST'], ['T',1,'T(0-100m)'] ,['T',2, 'T(0-1000m)']], 
            [['S',0,'SSS'], ['S',1,'S(0-100m)'],['S',2,'S(0-1000m)']], 
            [['H',0,'$\eta$']], 
            [['U',0,'KE(0m)'], ['U',1,'KE(15m)'], ['U',2,'KE(500m)'], ['H',1,'KE(geo)']] 
          ]

def_ylabels=[['Temperature', '($\deg$C)','T'], ['Salinity', '(PSU)','S'], ['Sea Surface Height', '(m)','H'], ['Kinetic Energy', '(m$^2$/s$^2$)','U']]
def_ylabels=[['Temperature', '(C)','T'], ['Salinity', '(PSU)','S'], ['Sea Surface Height', '(m)','H'], ['Kinetic Energy', '(m2/s2)','U']]

def_time=[datetime.datetime(2019,3,13), datetime.datetime(2020,12,30)]

plt.rc('text', usetex=False)
read_dia.plot_multi_timeseries(outprefix='PLOTS/G5v4.', pdirs=['TFIG','UFIG'], labels=['GEM5', 'GEM4'], plots=def_plots, ylabels=def_ylabels, time_range=None)

def_plots=[ [ ['T',1,'T(0-100m)'] ] ]

def_ylabels=[['Temperature', '(C)', 'T' ]]

read_dia.plot_multi_timeseries(outprefix='PLOTS/G5v4_T100', pdirs=['TFIG','UFIG'], labels=['GEM5', 'GEM4'], plots=def_plots, ylabels=def_ylabels, time_range=None)
