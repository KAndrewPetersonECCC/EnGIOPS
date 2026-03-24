import numpy as np
import matplotlib.pyplot as plt
P = np.arange(0,1.01,0.01)
fig, ax = plt.subplots()
ax.plot(P, P*(1-P), color='r', label='SPS')
IIEEM=np.zeros(P.shape)
IIEEM[:50]=P[:50]
IIEEM[50:]=1-P[50:]
ax.plot(P, IIEEM, color='g', label='IIEE(Median)')
ax.plot(P, 2*P*(1-P), color='b', label='<IIEE>')
ax.legend()
ax.set_xlabel('Probability')
ax.set_xlim([0, 1])
ax.set_ylim([0, 0.5])
fig.savefig('BestSPS.pdf')
