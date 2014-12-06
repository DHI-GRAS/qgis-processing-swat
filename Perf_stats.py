"""
***************************************************************************
   Pref_stats.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

#-------------------------------------------------------------------------------
# Name:        Prediction assembly
# Purpose:     Extracts time series of n-day ahead predictions from a series of
#              assimilation runs and evaluates their performance
#
# Author:      Peter Bauer-Gottwein, pbau@env.dtu.dk
#
# Created:     18-03-2014
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


PREDICTION_FOLDER ='p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\Test_Predictions' #Predictions will be stored here
OBS_FILE = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations

OUTSPECS = SWAT_output_format_specs()

#-------------------------Performance statistics------------------------------------
#Load observed data
if os.path.isfile(OBS_FILE):
    Q_obs = ReadObsFlowsAss(OBS_FILE)
    Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
for jj in range(0,8,1):
    obstimes = Q_obs[:,0]
    obstimes = obstimes[~numpy.isnan(Q_obs[:,1])]
    obs = Q_obs[~numpy.isnan(Q_obs[:,1]),1]
    obs_mean = numpy.mean(numpy.ma.masked_array(obs,numpy.isnan(obs)))

    #Loading the simulated data

    data = genfromtxt(PREDICTION_FOLDER + os.sep + 'day_' + str(jj) + '_ass.csv', delimiter=',')
    q_ass = data[:,1]
    std_ass = data[:,2]
    data = genfromtxt(PREDICTION_FOLDER + os.sep + 'day_' + str(jj) + '_det.csv', delimiter=',')
    q_det = data[:,1]
    std_det = data[:,2]
    dates = data[:,0]

    #Creating the bounds
    up_bound_det = q_det+2*std_det
    up_bound_ass = q_ass+2*std_ass

    low_bound_det = q_det-2*std_det
    low_bound_ass = q_ass-2*std_ass

    #Nash-Sutcliffe and RMSE
    nobs = len(obstimes)
    simobs = numpy.zeros(nobs)
    simobs_ass = numpy.zeros(nobs)
    stdobs = numpy.zeros(nobs)
    stdobs_ass = numpy.zeros(nobs)
    lastobs = numpy.zeros(nobs)
    numdates = dates
    for i in range(0,nobs):
        extractsim=q_det[numdates==obstimes[i]]
        extractsim_ass = q_ass[numdates==obstimes[i]]
        extractstd=std_det[numdates==obstimes[i]]
        extractstd_ass = std_ass[numdates==obstimes[i]]
        extractlastobs = obs[obstimes == obstimes[i]-jj]
        if len(extractsim) == 1:
            simobs[i] = extractsim[0]
            simobs_ass[i] = extractsim_ass[0]
        else:
            simobs[i] = numpy.nan
            simobs_ass[i] = numpy.nan
        if len(extractstd) == 1:
            stdobs[i] = extractstd[0]
            stdobs_ass[i] = extractstd_ass[0]
        else:
            stdobs[i] = numpy.nan
            stdobs_ass[i] = numpy.nan
        if len(extractlastobs) == 1:
            lastobs[i] = extractlastobs[0]
        else:
            lastobs[i] = numpy.nan


    indeces = ~numpy.isnan(stdobs)
    obs = obs[indeces]
    obstimes = obstimes[indeces]
    simobs = simobs[indeces]
    simobs_ass = simobs_ass[indeces]
    stdobs = stdobs[indeces]
    stdobs_ass = stdobs_ass[indeces]
    lastobs = lastobs[indeces]
    nobs = len(obs)

    meanobs = obs.mean()
    errorsimobs = simobs-obs
    errorsimobs_ass = simobs_ass-obs
    errorsimobsabs = numpy.absolute(errorsimobs)
    errorsimobsabs_ass = numpy.absolute(errorsimobs_ass)
    meanerror = errorsimobs.mean()
    meanerror_ass = errorsimobs_ass.mean()
    meanerrorpercent = meanerror/meanobs* 100
    meanerrorpercent_ass = meanerror_ass/meanobs* 100
    maerror = errorsimobsabs.mean()
    maerror_ass = errorsimobsabs_ass.mean()
    varobs = obs - meanobs
    rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
    rmsepercent = rmse/meanobs*100
    rmse_ass = numpy.sqrt(numpy.power(errorsimobs_ass,2).mean())
    rmsepercent_ass = rmse_ass/meanobs*100
    nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
    nse_ass = 1 - numpy.power(errorsimobs_ass,2).sum()/numpy.power(varobs,2).sum()

    #Coverage
    test = simobs-1.96*stdobs
    test2 = simobs+1.96*stdobs
    j=0
    for i in range(0,len(obs)):
        if test[i]<obs[i] and obs[i]<test2[i]:
            j = j+1

    test3 = simobs_ass-2*stdobs_ass
    test4 = simobs_ass+2*stdobs_ass
    j1 = 0
    for i in range(0,len(obs)):
        if test3[i]<obs[i] and obs[i]<test4[i]:
            j1 = j1+1

    if len(obs)>0:
        #Coverage
        covDet_withbase = float(j)/float(len(obs))*100
        covAss_withbase = float(j1)/float(len(obs))*100
    else:
        covDet_withbase = -999
        covAss_withbase = -999

    #Sharpness
    ll = simobs-1.96*stdobs
    ul = simobs+1.96*stdobs

    llass = simobs_ass-1.96*stdobs_ass
    ulass = simobs_ass+1.96*stdobs_ass


    sharpdet = numpy.mean(numpy.ma.masked_array((ul-ll),numpy.isnan(ul-ll)))
    sharpass = numpy.mean(numpy.ma.masked_array((ulass-llass),numpy.isnan(ulass-llass)))

    sharpdiff = (sharpdet-sharpass)/sharpdet

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

    issass = zeros([len(ll)])

    for o in range(0,len(llass)):
        if llass[o] > obs[o]:
            issass[o] = 1/float(len(llass))*(ulass[o]-llass[o]+2/alpha*(llass[o]-obs[o]))
        elif ulass[o] < obs[o]:
            issass[o] = 1/float(len(llass))*(ulass[o]-llass[o]+2/alpha*(obs[o]-ulass[o]))
        else:
            issass[o] = 1/float(len(llass))*(ulass[o]-llass[o])


    ISS = nansum(iss)
    ISSass = nansum(issass)

    # Continuous ranked probability score (CRPS) See Gneiting et al, 2005, equation 4

    crps = zeros([len(simobs)])
    crps_ass = zeros([len(simobs)])

    for i in range(0,len(simobs)):
        mu = simobs[i]
        sigma = stdobs[i]
        mu_ass = simobs_ass[i]
        sigma_ass = stdobs_ass[i]
        criterion = (obs[i]-mu)/sigma
        criterion_ass = (obs[i]-mu_ass)/sigma_ass
        pdfc = 1.0/(2.0*math.pi)**(.5)*math.exp(-1/2*criterion**2)
        pdfc_ass = 1.0/(2.0*math.pi)**(.5)*math.exp(-1/2*criterion_ass**2)
        cdfc = 1.0/2.0*(1+math.erf(criterion/2**(.5)))
        cdfc_ass = 1.0/2.0*(1+math.erf(criterion_ass/2**(.5)))
        crps[i] = sigma*(criterion*(2.0*cdfc - 1.0) + 2.0*pdfc - 1.0/math.pi**(.5))
        crps_ass[i] = sigma_ass*(criterion_ass*(2.0*cdfc_ass - 1.0) + 2.0*pdfc_ass - 1.0/math.pi**(.5))
        #print(mu,sigma,obs[i],criterion,pdfc,cdfc,crps[i])

    CRPS = nanmean(crps)
    CRPS_ass = nanmean(crps_ass)

    indeces = ~numpy.isnan(lastobs)
    obs = obs[indeces]
    obstimes = obstimes[indeces]
    lastobs = lastobs[indeces]
    simobs = simobs[indeces]
    simobs_ass = simobs_ass[indeces]
    stdobs = stdobs[indeces]
    stdobs_ass = stdobs_ass[indeces]
    varobs = obs - lastobs
    varobsabs = numpy.absolute(varobs)
    maepersistence = varobsabs.mean()
    errorsimobs = simobs-obs
    errorsimobs_ass = simobs_ass-obs
    nobspi = len(obs)
    piindex = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
    piindex_ass = 1 - numpy.power(errorsimobs_ass,2).sum()/numpy.power(varobs,2).sum()

    #Creating result file
    f = open(PREDICTION_FOLDER + os.sep + 'results_day_' + str(jj) + ".txt", "w")
    f.write('Number of predicted observations' + '\n')
    f.write(str(nobs)+ '\n')
    f.write('Mean of predicted observations (m3/s)' + '\n')
    f.write(str(meanobs)+ '\n')
    f.write('Coverage of the nominal 95% interval (%)' + '\n')
    f.write('Deterministic run       ' + str(covDet_withbase)+ '\n')
    f.write('Assimilation run        ' + str(covAss_withbase)+ '\n')
    f.write('RMSE (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(rmse)+ '\n')
    f.write('Assimilation run        ' + str(rmse_ass)+ '\n')
    f.write('ME (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(meanerror)+ '\n')
    f.write('Assimilation run        ' + str(meanerror_ass)+ '\n')
    f.write('MAE (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(maerror)+ '\n')
    f.write('Assimilation run        ' + str(maerror_ass)+ '\n')
    f.write('Nash-Sutcliffe Efficiency' + '\n')
    f.write('Deterministic run       ' + str(nse)+ '\n')
    f.write('Assimilation run        ' + str(nse_ass)+ '\n')
    f.write('Sharpness (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(sharpdet)+ '\n')
    f.write('Assimilation run        ' + str(sharpass)+ '\n')
    f.write('Interval Skill Score (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(ISS)+ '\n')
    f.write('Assimilation run        ' + str(ISSass)+ '\n')
    f.write('Persistence Index' + '\n')
    f.write('Deterministic run       ' + str(piindex)+ '\n')
    f.write('Assimilation run        ' + str(piindex_ass)+ '\n')
    f.write('MAE Persistence (m3/s)' + '\n')
    f.write('MAE of persistence       ' + str(maepersistence)+ '\n')
    f.write('Continous Ranked Probability Score (m3/s)' + '\n')
    f.write('Deterministic run       ' + str(CRPS)+ '\n')
    f.write('Assimilation run        ' + str(CRPS_ass)+ '\n')
    f.close()