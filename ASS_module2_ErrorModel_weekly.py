"""
***************************************************************************
   ASS_module2_ErrorModel_weekly.py
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
from ASS_utilities import ReadObsFlowsAss
from ASS_utilities import LoadData
from ASS_utilities import MuskSetupFlows
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()

def BaseRun(Ass_folder, nbrch, Enddate, Startdate):

    days = int(Enddate-Startdate)+1

    #Getting Muskingum Parameters
    (F,Ga,Gb) = MuskSetupFlows(Ass_folder, nbrch, Enddate, Startdate)

    #Getting input data and parameters
    (X,K,drainsTo,alphaerr,q,RR,nbrch_add, timestep,loss) = LoadData(Ass_folder, nbrch, Enddate, Startdate)

    #Fitting the RR to the timestep
    Inputs = numpy.zeros([days*(1/timestep),nbrch_add])
    for i in range(0,days):
        for k in range (0,int(1/timestep)):
            Inputs[1/timestep*i+k,:] = RR[i]

    simlength = len(Inputs)

    xtemp = numpy.zeros([nbrch_add])
    x = numpy.zeros([nbrch_add,simlength])

    for i in range(1,simlength):
        x[:,i] = dot(F,xtemp)+dot(Ga,Inputs[i-1,:].T)+dot(Gb,Inputs[i,:].T)
        xtemp = x[:,i]

    #Adjust to one flow per day
    q_out = numpy.zeros([nbrch_add,days])
    for i in range(0,days):
        q_out_temp = 0
        for j in range(0,int(1/timestep)):
            q_out_temp = q_out_temp + x[:,i*(1/timestep)+j]
        q_out[:,i] = q_out_temp/(1/timestep)

    return(q_out)

def ErrorModel_discharge(obs_file, Ass_folder, nbrch, Enddate, Startdate):
    """Fits an AR1 model to the time series"""

    #Load observed data
    Q_obs = ReadObsFlowsAss(obs_file)
    Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
    Q_obs = Q_obs[find(Q_obs[:,0] >= Startdate),:]
    reachID = []
    reachID.append(Q_obs[0,3])
    for i in range(1,len(Q_obs)):
        if Q_obs[i,3] != reachID[-1]:
            reachID.append(Q_obs[i,3])

    for n in range(0,len(reachID)):
        #Get simulated data
        q_out = BaseRun(Ass_folder, nbrch, Enddate, Startdate)
        sim_daily = q_out[int(reachID[n])-1,:]

        # Compute weekly values
        sim = []
        obs = []
        for i in range(0,len(sim_daily)/7):
            if numpy.sum(numpy.isnan(Q_obs[i*7:(i+1)*7,1])) > 2:
                sim.append(numpy.mean(sim_daily[i*7:(i+1)*7]))
                obs.append(numpy.nan)
            else:
                sim.append(numpy.mean(sim_daily[i*7:(i+1)*7]))
                obs.append(numpy.mean(numpy.ma.masked_array(Q_obs[i*7:(i+1)*7,1],numpy.isnan(Q_obs[i*7:(i+1)*7,1]))))

        print('Number of weeks without observed data: ' + str(sum(numpy.isnan(obs))))

        #Excluding weeks with no observed flow and zero flow
        sim_weekly = numpy.array(sim)
        obs_weekly = numpy.array(obs)
        obs_weekly[find(numpy.isnan(obs))] = -1
        a = numpy.where(obs_weekly>0)
        ts = numpy.zeros([len(a[0])])
        for i in range(0,len(a[0])):
            ts[i] = (sim_weekly[a[0][i]]-obs_weekly[a[0][i]])/(obs_weekly[a[0][i]])

        # Estimate alpha
        x = ts[0:-1]
        y = ts[1:]
        p = polyfit(x,y,1)
        alpha = p[0]

        # Estimate sigma from the residuals of the regression.
        yhat = polyval(p,x)
        sigma = std(y-yhat)

        with open(Ass_folder + os.sep + 'ErrorModelReach' + str(int(reachID[n])) + '_weekly.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(['alphaerr']+['q'])
            file_writer.writerow([str(alpha)]+[str(sigma)])
