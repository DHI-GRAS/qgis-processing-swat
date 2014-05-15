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

    days = int(Enddate-Startdate)

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
    Q_obs_Startdate = Q_obs[0,0]
    if sum(Q_obs[:,0] <= Enddate-8) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] <= Enddate-8),:]

    reachID = []
    reachID.append(Q_obs[0,3])
    for i in range(1,len(Q_obs)):
        if Q_obs[i,3] != reachID[-1]:
            reachID.append(Q_obs[i,3])

    for n in range(0,len(reachID)):
        #Get simulated data
        q_out = BaseRun(Ass_folder, nbrch, Enddate, Startdate)
        DeltaStart = Q_obs_Startdate-Startdate
        sim = q_out[int(reachID[n])-1,DeltaStart:]

        #Excluding zeroflow and missing data
        Q_obs[find(numpy.isnan(Q_obs[:,1])==1)] = -1
        a = numpy.where(Q_obs[:,1]>0)
        ts = numpy.zeros([len(a[0])])
        for i in range(0,len(a[0])):
            ts[i] = (sim[a[0][i]]-Q_obs[a[0][i],1])/(Q_obs[a[0][i],1])

        # Estimate alpha
        x = ts[0:-1]
        y = ts[1:]
        N = len(x)
        Sxx = sum(x**2.)-sum(x)**2./N
        Syy = sum(y**2.)-sum(y)**2./N
        Sxy = sum(x*y)-sum(x)*sum(y)/N
        a = Sxy/Sxx
        b = mean(y)-a*mean(x)
        alpha = a

        # Estimate sigma from the residuals of the regression.
        yhat = a*x + b
        sigma = std(y-yhat)

        with open(Ass_folder + os.sep + 'ErrorModelReach' + str(int(reachID[n])) + '.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(['alphaerr']+['q'])
            file_writer.writerow([str(alpha)]+[str(sigma)])
