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
import ASS_Evaluation

PREDICTION_FOLDER ='r:\\Projects\\TigerNET\\Kavango\\Assimilation\\F_Predictions_modified' #Predictions will be stored here
SRC_FOLDER = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\TxtInOut' #SWAT output folder
OBS_FILE = 'r:\\Projects\\TigerNET\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations
OBS_FILE_ASS = 'r:\\Projects\\TigerNET\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv'
NBRCH = 12 #number of reaches in the model
REACH_ID = 10 #reach for which in-situ data is available

OUTSPECS = SWAT_output_format_specs()

#Get startdate from SWAT file.cio and compare with startdate of assimilation to determine header in SWAT output files
SWAT_time_info = read_SWAT_time(SRC_FOLDER)
SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
if SWAT_time_info[4] > 0: # Account for NYSKIP>0
    SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1

ASS_startdate = SWAT_startdate
ASS_enddate = SWAT_enddate
arraylen = 5000
count = 0
day_0_det = numpy.zeros([arraylen,3])
day_1_det = numpy.zeros([arraylen,3])
day_2_det = numpy.zeros([arraylen,3])
day_3_det = numpy.zeros([arraylen,3])
day_4_det = numpy.zeros([arraylen,3])
day_5_det = numpy.zeros([arraylen,3])
day_6_det = numpy.zeros([arraylen,3])
day_7_det = numpy.zeros([arraylen,3])

day_0_ass = numpy.zeros([arraylen,3])
day_1_ass = numpy.zeros([arraylen,3])
day_2_ass = numpy.zeros([arraylen,3])
day_3_ass = numpy.zeros([arraylen,3])
day_4_ass = numpy.zeros([arraylen,3])
day_5_ass = numpy.zeros([arraylen,3])
day_6_ass = numpy.zeros([arraylen,3])
day_7_ass = numpy.zeros([arraylen,3])

dates = range(int(ASS_startdate), int(ASS_enddate)+1,1)
dates = numpy.array(dates)
dates.reshape(len(dates),1)

today = date.today()
period = today-date(2012,01,01) + timedelta(1)
enddays = period.days

# Loop through each day of validation period
# In 2012 observations are available between 01-Jan and 30-Sep (Range 0..274)

#--------------------------Plotting----------------------------------------
for jj in range(0,8,1):
    #Getting the observed data and identify reach(es)
    if os.path.isfile(OBS_FILE):
        Q_obs = ReadObsFlowsAss(OBS_FILE)
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        reachID = []
        reachID.append(Q_obs[0,3])
        for i in range(1,len(Q_obs)):
            if Q_obs[i,3] != reachID[-1]:
                reachID.append(Q_obs[i,3])
    else:
        reachID = [rch_ID]

    for n in range(0,len(reachID)):

        #Routed simulation data
        data = genfromtxt(PREDICTION_FOLDER + os.sep + 'day_' + str(jj) + '_ass.csv', delimiter=',')
        q_ass = data[:,1]
        std_ass = data[:,2]
        dates = data[:,0]

        #Creating the bounds
        up_bound_ass = q_ass+2*std_ass
        low_bound_ass = numpy.zeros([len(q_ass)])
        for j in range (0,len(q_ass)):
            if q_ass[j]-2*std_ass[j]>0:
                low_bound_ass[j] = q_ass[j]-2*std_ass[j]
            else:
                low_bound_ass[j] = 0

        # Create plot

        fig = plt.figure()
        plt.title('Assimilation results for reach  '+str(int(reachID[n])), fontsize=12)
        plt.ylabel('Discharge [$m^3/s$]')
        p1, = plt.plot_date(dates, q_ass, linestyle='-',color='green', marker = 'None')
        plt.plot_date(dates, low_bound_ass, linestyle='--', color = 'green',marker = 'None')
        plt.plot_date(dates, up_bound_ass, linestyle='--', color = 'green',marker = 'None')
        if os.path.isfile(OBS_FILE):
            # Extract obsdata for current reachID
            obsdata = Q_obs[find(Q_obs[:,3]==int(reachID[n])),:]
            obstimes = obsdata[:,0]
            obs_dates = obstimes
            p2, = plt.plot_date(obs_dates, obsdata[:,1], color='red', marker = '.')
            plt.legend([p1,p2],['Assimilated Run','Observed'])
        plt.legend(loc=0)
        ax1 = fig.add_subplot(111)
        ax1.fill_between(dates, low_bound_ass, up_bound_ass, color='green',alpha=.3)
        plt.ylim([0,max(up_bound_ass[~numpy.isnan(up_bound_ass)])+5])
        plt.xlim([min(dates),max(dates)])
        figname = PREDICTION_FOLDER + os.sep + 'day_' + str(jj) + '_ass.pdf'
        plt.savefig(figname)
#        plt.show()

#-------------------------Performance statistics------------------------------------
for jj in range(0,8,1):
    #Load observed data
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
    meanerror = errorsimobs.mean()
    meanerror_ass = errorsimobs_ass.mean()
    meanerrorpercent = meanerror/meanobs* 100
    meanerrorpercent_ass = meanerror_ass/meanobs* 100
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
    for i in range(0,len(obs)-1):
        if test[i]<obs[i] and obs[i]<test2[i]:
            j = j+1

    test3 = simobs_ass-2*stdobs_ass
    test4 = simobs_ass+2*stdobs_ass
    j1 = 0
    for i in range(0,len(obs)-1):
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
    f.write('Continous Ranked Probability Score' + '\n')
    f.write('Deterministic run       ' + str(CRPS)+ '\n')
    f.write('Assimilation run        ' + str(CRPS_ass)+ '\n')
    f.close()