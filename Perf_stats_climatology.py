#-------------------------------------------------------------------------------
# Name:        Prediction assembly
# Purpose:     Extracts time series of n-day ahead predictions from a series of
#              assimilation runs and evaluates their performance
#
# Author:      Peter Bauer-Gottwein, pbau@env.dtu.dk
#
# Created:     18-03-2014
# Copyright:   (c) pbau 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import csv
import numpy
from datetime import date, timedelta
from matplotlib.pylab import *
import subprocess
from PyQt4 import QtGui
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadObsFlowsAss


climatology_res_filename ='p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\Test_Predictions\\perf_climatology.txt' #Results will be stored here
OBS_FILE = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations
CLIMATOLOGY_FILE = 'p:\ACTIVE\TigerNET 30966 PBAU\Publications\OF_Paper\Revision_1\Processing\climatology_Rundu_val.csv' # file with climatology


OUTSPECS = SWAT_output_format_specs()


#-------------------------Performance statistics------------------------------------
#Load observed data
if os.path.isfile(OBS_FILE):
    Q_obs = ReadObsFlowsAss(OBS_FILE)
    Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
obstimes = Q_obs[:,0]
obstimes = obstimes[~numpy.isnan(Q_obs[:,1])]
obs = Q_obs[~numpy.isnan(Q_obs[:,1]),1]
obs_mean = numpy.mean(numpy.ma.masked_array(obs,numpy.isnan(obs)))

#Loading the climatology data

data = genfromtxt(CLIMATOLOGY_FILE, delimiter=',')
q = data[:,1]
std = data[:,2]
dates = data[:,0] + OUTSPECS.PYEX_DATE_OFFSET

#Creating the bounds
up_bound= q+2*std

low_bound = q-2*std

#Nash-Sutcliffe and RMSE
nobs = len(obstimes)
simobs = numpy.zeros(nobs)
stdobs = numpy.zeros(nobs)
numdates = dates
for i in range(0,nobs):
    extractsim=q[numdates==obstimes[i]]
    extractstd=std[numdates==obstimes[i]]
    if len(extractsim) == 1:
        simobs[i] = extractsim[0]
    else:
        simobs[i] = numpy.nan
    if len(extractstd) == 1:
        stdobs[i] = extractstd[0]
    else:
        stdobs[i] = numpy.nan

indeces = ~numpy.isnan(stdobs)
obs = obs[indeces]
obstimes = obstimes[indeces]
simobs = simobs[indeces]
stdobs = stdobs[indeces]
nobs = len(obs)

meanobs = obs.mean()
errorsimobs = simobs-obs
errorsimobsabs = numpy.absolute(errorsimobs)
meanerror = errorsimobs.mean()
meanerrorpercent = meanerror/meanobs* 100
maerror = errorsimobsabs.mean()
varobs = obs - meanobs
rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
rmsepercent = rmse/meanobs*100
nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
#Coverage
test = simobs-1.96*stdobs
test2 = simobs+1.96*stdobs
j=0
for i in range(0,len(obs)):
    if test[i]<obs[i] and obs[i]<test2[i]:
        j = j+1

if len(obs)>0:
    #Coverage
    covDet_withbase = float(j)/float(len(obs))*100
else:
    covDet_withbase = -999

#Sharpness
ll = simobs-1.96*stdobs
ul = simobs+1.96*stdobs
sharpdet = numpy.mean(numpy.ma.masked_array((ul-ll),numpy.isnan(ul-ll)))

#Interval Skill Score
alpha = 0.05     #significance level
iss = zeros([len(ll)])

for o in range(0,len(ll)):
    if ll[o] > obs[o]:
        iss[o] = 1/float(len(ll))*(ul[o]-ll[o]+2/alpha*(ll[o]-obs[o]))
    elif ul[o] < obs[o]:
        iss[o] = 1/float(len(ll))*(ul[o]-ll[o]+2/alpha*(obs[o]-ul[o]))
    else:
        iss[o] = 1/float(len(ll))*(ul[o]-ll[o])

ISS = nansum(iss)

# Continuous ranked probability score (CRPS) See Gneiting et al, 2005, equation 4

crps = zeros([len(simobs)])


for i in range(0,len(simobs)):
    mu = simobs[i]
    sigma = stdobs[i]
    criterion = (obs[i]-mu)/sigma
    pdfc = 1.0/(2.0*math.pi)**(.5)*math.exp(-1/2*criterion**2)
    cdfc = 1.0/2.0*(1+math.erf(criterion/2**(.5)))
    crps[i] = sigma*(criterion*(2.0*cdfc - 1.0) + 2.0*pdfc - 1.0/math.pi**(.5))
    #print(mu,sigma,obs[i],criterion,pdfc,cdfc,crps[i])

CRPS = nanmean(crps)

#Creating result file
f = open(climatology_res_filename, "w")
f.write('Number of predicted observations' + '\n')
f.write(str(nobs)+ '\n')
f.write('Mean of predicted observations (m3/s)' + '\n')
f.write(str(meanobs)+ '\n')
f.write('Coverage of the nominal 95% interval (%)' + '\n')
f.write('Deterministic run       ' + str(covDet_withbase)+ '\n')
f.write('RMSE (m3/s)' + '\n')
f.write('Deterministic run       ' + str(rmse)+ '\n')
f.write('ME (m3/s)' + '\n')
f.write('Deterministic run       ' + str(meanerror)+ '\n')
f.write('MAE (m3/s)' + '\n')
f.write('Deterministic run       ' + str(maerror)+ '\n')
f.write('Nash-Sutcliffe Efficiency' + '\n')
f.write('Deterministic run       ' + str(nse)+ '\n')
f.write('Sharpness (m3/s)' + '\n')
f.write('Deterministic run       ' + str(sharpdet)+ '\n')
f.write('Interval Skill Score (m3/s)' + '\n')
f.write('Deterministic run       ' + str(ISS)+ '\n')
f.write('Continous Ranked Probability Score (m3/s)' + '\n')
f.write('Deterministic run       ' + str(CRPS)+ '\n')
f.close()