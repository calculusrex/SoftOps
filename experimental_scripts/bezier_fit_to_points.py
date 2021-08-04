import matplotlib.pyplot as plt
import numpy as np
from scipy.special import comb as n_over_k

Mtk = lambda n, t, k: t**k * (1-t)**(n-k) * n_over_k(n,k)
BézierCoeff = lambda ts: [[Mtk(3,t,k) for k in range(4)] for t in ts]

fcn np.log
tPlot = np.linspace(0. ,1. , 81)
xPlot = np.linspace(0.1,2.5, 81)
tData = tPlot[0:81:10]
xData = xPlot[0:81:10]
data = np.column_stack((xData, fcn(xData))) # shapes (9,2)

Pseudoinverse = np.linalg.pinv(BézierCoeff(tData)) # (9,4) -> (4,9)
control_points = Pseudoinverse.dot(data)     # (4,9)*(9,2) -> (4,2)
Bézier = np.array(BézierCoeff(tPlot)).dot(control_points)
residuum = fcn(Bézier[:,0]) - Bézier[:,1]

fig, ax = plt.subplots()
ax.plot(xPlot, fcn(xPlot),   'r-')
ax.plot(xData, data[:,1],    'ro', label='input')
ax.plot(Bézier[:,0],
                Bézier[:,1],         'k-', label='fit')
ax.plot(xPlot, 10.*residuum, 'b-', label='10*residuum')
ax.plot(control_points[:,0],
                control_points[:,1], 'ko:', fillstyle='none')
ax.legend()
fig.show()


# manual_points = np.array([[0.1,np.log(.1)],[.27,-.6],[.82,.23],[2.5,np.log(2.5)]])
# Bézier = np.array(BézierCoeff(tPlot)).dot(manual_points)
# residuum = fcn(Bézier[:,0]) - Bézier[:,1]

# fig, ax = plt.subplots()
# ax.plot(xPlot, fcn(xPlot),   'r-')
# ax.plot(xData, data[:,1],    'ro', label='input')
# ax.plot(Bézier[:,0],
#                 Bézier[:,1],         'k-', label='fit')
# ax.plot(xPlot, 10.*residuum, 'b-', label='10*residuum')
# ax.plot(manual_points[:,0],
#                 manual_points[:,1],  'ko:', fillstyle='none')
# ax.legend()
# fig.show()
