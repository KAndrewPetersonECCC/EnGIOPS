from importlib import reload
import sys
import os

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import shapiro

dx=25
DX=1000
NX=DX/dx
L = dx*(np.arange(NX*100)+1)/100
NPass = np.arange(500)+1

MaxFilter = []
for N in NPass:
   Max, __ = shapiro.SHAPIRO_CUTOFF(L, N, dx=dx)
   MaxFilter.append(Max)

#Max10, __ = shapiro.SHAPIRO_CUTOFF(L, 10, dx=dx)
#Max30, __ = shapiro.SHAPIRO_CUTOFF(L, 30, dx=dx)
Max75, __ = shapiro.SHAPIRO_CUTOFF(L, 75, dx=dx)
Max3C, __ = shapiro.SHAPIRO_CUTOFF(L, 300, dx=dx)  

fig, axe = plt.subplots()
axe.plot(MaxFilter, NPass, 'k')
#axe.plot([0, Max10, Max10], [10, 10, 0], 'c', label='N=10')
#axe.plot([0, Max30, Max30], [30, 30, 0], 'g', label='N=30')
axe.plot([0, Max75, Max75], [75, 75, 0], 'b', label='N=75')
axe.plot([0, Max3C, Max3C], [300, 300, 0], 'r', label='N=300')
axe.set_xlim([0, 25*40])
axe.set_ylim([0, 500])
axe.legend()
axe.set_xlabel('Lengthscale')
axe.set_ylabel('N Pass')
axe.set_title('Maximum Length Scale Attenuated > 99%')
fig.savefig('Pass.pdf')

#RES10 = shapiro.SHAPIRO_RETURN(L, 10, dx=dx)
#RES30 = shapiro.SHAPIRO_RETURN(L, 30, dx=dx)
RES75 = shapiro.SHAPIRO_RETURN(L, 75, dx=dx)
RES3C = shapiro.SHAPIRO_RETURN(L, 300, dx=dx)

fig, axe = plt.subplots()
ivalid = np.where(L> 2*dx)
#axe.plot(L[ivalid], RES10[ivalid], 'c', label='N=10')
#axe.plot(L[ivalid], RES30[ivalid], 'g', label='N=30')
axe.plot(L[ivalid], RES75[ivalid], 'b', label='N=75')
axe.plot(L[ivalid], RES3C[ivalid], 'r', label='N=300')
#axe.plot([0, Max10, Max10], [0.01, 0.01, 0.0], 'k')
#axe.plot([0, Max30, Max30], [0.01, 0.01, 0.0], 'k')
axe.plot([0, Max75, Max75], [0.01, 0.01, 0.0], 'k')
axe.plot([0, Max3C, Max3C], [0.01, 0.01, 0.0], 'k')
axe.set_xlim([0, 25*40])
axe.set_ylim([0, 0.1])
axe.legend()

#print('N=10  : ', Max10, 'km')
#print('N=30  : ', Max30, 'km')
print('N=75  : ', Max75, 'km')
print('N=300 : ', Max3C, 'km')

axe.set_xlabel('Lengthscale')
axe.set_ylabel('Return')
axe.set_title('Response Function')
fig.savefig('Resp.pdf')
