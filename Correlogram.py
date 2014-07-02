import os
import csv
import numpy
from datetime import date, timedelta
from matplotlib.pylab import *
import subprocess
from PyQt4 import QtGui
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadNoSubs
import ASS_module3_Assimilation
import ASS_module1_PrepData
import ASS_module2_ErrorModel
import ASS_module4_Results
from ASS_utilities import ReadObsFlowsAss
import ASS_Evaluation

#Load observed data
Q_obs = ReadObsFlowsAss(obs_file)
Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
Q_obs = Q_obs[find(Q_obs[:,0] >= Startdate),:]

##Q_obs[1:100,1]=NaN       # Removes 2005.02.15 - 2005.05.25
##Q_obs[670:995,1]=NaN     # Remves 2006.12.16 - 2007.11.06, no flow
##Q_obs[0:1416,1]=NaN     # Remves 2005.02.15 - 2009.01.01, no flow


#Get simulated data
q_out = BaseRun(Ass_folder, nbrch, Enddate, Startdate)
sim = q_out[int(ReachNo)-1,:]

#Excluding zeroflow and missing data
Q_obs[find(numpy.isnan(Q_obs[:,1])==1)] = -1
a = numpy.where(Q_obs[:,1]>0)
ts = numpy.zeros([len(a[0])])
for i in range(0,len(a[0])):
    ts[i] = (sim[a[0][i]]-Q_obs[a[0][i],1])/Q_obs[a[0][i],1]

# Estimate alpha
x = ts[0:-1]
y = ts[1:]
p = polyfit(x,y,1)
alpha = p[0]

# Estimate sigma from the residuals of the regression.
yhat = polyval(p,x)
sigma = std(y-yhat)

AR_res = y-yhat


N = float(len(AR_res))

#Correlogram

rh = numpy.zeros([len(AR_res)])

ch_sum = numpy.zeros([len(AR_res)])
co_sum = numpy.zeros([len(AR_res)])

ch = numpy.zeros([len(AR_res)])
co = numpy.zeros([len(AR_res)])

for h in range (0,int(N)):
    for i in range (0,int(N)-h):
        ch_sum[i] = (AR_res[i]-mean(AR_res))*(AR_res[i+h]-mean(AR_res))
        ch[i] = 1/N*sum(ch_sum[0:i])
    for j in range (0,int(N)):
        co_sum[j] = (AR_res[j]-mean(AR_res))**2
        co[j] = 1/N*sum(co_sum[0:j])

    rh[h] = ch[i]/co[j]

ul = ones([len(rh)])*( -1/float(N)+1.96/N**(0.5))
ll = ones([len(rh)])*( -1/float(N)-1.96/N**(0.5))

count = 0
for i in range(0,len(rh)):
        if ul[i]<rh[i] or rh[i]<ll[i]:
            count = count + 1

pct = count/float(len(rh))

fig = matplotlib.pyplot.figure(figsize=(4.5, 3.5))

matplotlib.rcParams.update({'font.size': 8, 'font.family': 'sans'})

matplotlib.rc('ytick', labelsize=8)
matplotlib.rc('xtick', labelsize=8)

ylabel('Correlation coefficient')
xlabel('Lag [days]')

xlim([0,2200])

plot(rh, linestyle = '-', marker = '.', markersize = 2)
plot(ul, linestyle ='--', marker = 'None', color = 'black')
plot(ll, linestyle ='--', marker = 'None', color = 'black')

##figname = 'C:\Users\Gudny\Thesis\Writing\Figures\Correlogram_Mokolo.pdf'
##savefig(figname)

show()