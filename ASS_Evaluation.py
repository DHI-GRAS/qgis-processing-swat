"""
***************************************************************************
    ASS_Evaluation.py
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

# Import modules
from matplotlib.pylab import *
import numpy
import os
import csv
from datetime import date, timedelta
from ASS_utilities import ReadObsFlowsAss
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()

def Results(Startdate,Enddate, Ass_folder, nbrch, ReachNo, obs_file):

    #Load observed data
    obsdata =  numpy.genfromtxt(obs_file, delimiter = ',', skiprows=0, missing_values = 'NaN')
    obsdata[:,0] = obsdata[:,0] + OUTSPECS.PYEX_DATE_OFFSET
    obstimes = obsdata[:,0]
    obstimes = obstimes[~numpy.isnan(obsdata[:,1])]
    obs = obsdata[~numpy.isnan(obsdata[:,1]),1]
    obs_mean = numpy.mean(numpy.ma.masked_array(obs,numpy.isnan(obs)))

    #Loading the simulated data

    x2 = genfromtxt(Ass_folder + os.sep + 'Deterministic_Output.csv', delimiter=',')
    P2 = genfromtxt(Ass_folder + os.sep + 'Deterministic_Cov.csv', delimiter=',')
    x3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Output.csv', delimiter=',')
    P3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Cov.csv', delimiter=',')
    dates = range(int(Startdate), int(Enddate)+1,1)

    q_det = x2[ReachNo-1,:]
    q_ass = x3[ReachNo-1,:]
    std_det = P2[ReachNo-1,:]
    std_ass = P3[ReachNo-1,:]

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
    numdates = dates
    for i in range(0,nobs):
        extractsim=q_det[numdates==obstimes[i]]
        extractsim_ass = q_ass[numdates==obstimes[i]]
        extractstd=std_det[numdates==obstimes[i]]
        extractstd_ass = std_ass[numdates==obstimes[i]]
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
    obs = obs[~numpy.isnan(simobs)]
    obstimes = obstimes[~numpy.isnan(simobs)]
    simobs = simobs[~numpy.isnan(simobs)]
    simobs_ass = simobs_ass[~numpy.isnan(simobs_ass)]
    stdobs = stdobs[~numpy.isnan(stdobs)]
    stdobs_ass = stdobs_ass[~numpy.isnan(stdobs_ass)]
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
    test = simobs[1:len(simobs)]-2*stdobs
    test2 = simobs[1:len(simobs)]+2*stdobs
    j=0
    for i in range(0,len(obs)-1):
        if test[i]<obs[i] and obs[i]<test2[i]:
            j = j+1

    test3 = simobs_ass[1:len(simobs_ass)]-2*stdobs_ass
    test4 = simobs_ass[1:len(simobs_ass)]+2*stdobs_ass
    j1 = 0
    for i in range(0,len(obs)-1):
        if test3[i]<obs[i] and obs[i]<test4[i]:
            j1 = j1+1


    #Coverage
    covDet_withbase = float(j)/float(len(obs))*100
    covAss_withbase = float(j1)/float(len(obs))*100

    #Sharpness
    ll = simobs[1:len(simobs)]-1.96*stdobs
    ul = simobs[1:len(simobs)]+1.96*stdobs

    llass = simobs_ass[1:len(simobs_ass)]-1.96*stdobs_ass
    ulass = simobs_ass[1:len(simobs_ass)]+1.96*stdobs_ass


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

    #Creating result file
    f = open(Ass_folder + os.sep + 'results' + ".txt", "w")
    f.write('Coverage' + '\n')
    f.write('Deterministic run       ' + str(covDet_withbase)+ '\n')
    f.write('Assimilation run        ' + str(covAss_withbase)+ '\n')
    f.write('RMSE' + '\n')
    f.write('Deterministic run       ' + str(rmse)+ '\n')
    f.write('Assimilation run        ' + str(rmse_ass)+ '\n')
    f.write('Nash-Sutcliffe Efficiency' + '\n')
    f.write('Deterministic run       ' + str(nse)+ '\n')
    f.write('Assimilation run        ' + str(nse_ass)+ '\n')
    f.write('Sharpness' + '\n')
    f.write('Deterministic run       ' + str(sharpdet)+ '\n')
    f.write('Assimilation run        ' + str(sharpass)+ '\n')
    f.write('Interval Skill Score' + '\n')
    f.write('Deterministic run       ' + str(ISS)+ '\n')
    f.write('Assimilation run        ' + str(ISSass)+ '\n')
    f.close()


if __name__ == '__main__':
##    Ass_folder = 'c:\Users\Gudny\Thesis\Assimilation_Mokolo_Sub20_final\Assimilation_Mokolo_3dayAhead'                                   #Folder where results are stored
##    src_folder = 'c:\Users\Gudny\Thesis\Iris\sub20_final'                               #Folder with SWAT results
##    obs_file = 'c:\Users\Gudny\Thesis\Assimilation_Mokolo_Sub20_final\Assimilation_upstream_stations\A4H005.csv'                        #File with observed discharge data
##    nbrch = 26
##    ReachNo = 20                                                                   #Reach for which the results are computed

##    Ass_folder = 'c:\Users\Gudny\Thesis\Assimilation_Kavango_complete_inlet\Assimilation_Kavango_WOIS'
##    src_folder = 'c:\Users\Gudny\Thesis\Kavango\TxtInOut_complete_inlet'                                      #Folder with SWAT results
##    obs_file = 'c:\Users\Gudny\Thesis\Assimilation_Kavango_complete_inlet\Assimilation_Kavango_WOIS\Rundu.csv'               #Folder with observed discharge data
##    nbrch = 7
##    ReachNo = 5                #Reach for which the model is run

    #Get the startdate and endate from SWAT fil.cio and compare with startdate of data to determine header in output files
    deli = [10,7,8]
    Startdate = date2num(date(2005,2,15))
    Dates = genfromtxt(src_folder + os.sep + 'file.cio', skip_header = 7, delimiter = deli, usecols=1)
    Startdate_SWAT = date2num(date((int(Dates[1])-1),12,31))+Dates[2]
##    Enddate = date2num(date(int(Dates[1]+Dates[0]-1),1,1))+Dates[3]
    NYSKIP = Dates[52]                              # number of years skipped in output printing/summarization
    if NYSKIP > 0:
        Startdate_SWAT_results = date2num(date((int(Dates[1]+NYSKIP)),1,1))
        header = int((Startdate-Startdate_SWAT_results)*nbrch+9)
    else:
        header = 9

    Results(Startdate,Enddate, Ass_folder, nbrch, ReachNo)
