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

    relativeerror = False
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
        simobs = numpy.zeros([len(a[0])])
        obsobs = numpy.zeros([len(a[0])])
        for i in range(0,len(a[0])):
            if relativeerror:
                ts[i] = (sim[a[0][i]]-Q_obs[a[0][i],1])/(Q_obs[a[0][i],1])
                simobs[i] = sim[a[0][i]]
                obsobs[i] = Q_obs[a[0][i],1]
            else:
                ts[i] = (sim[a[0][i]]-Q_obs[a[0][i],1])
                simobs[i] = sim[a[0][i]]
                obsobs[i] = Q_obs[a[0][i],1]




        with open(Ass_folder + os.sep + 'simobs.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(simobs)


        with open(Ass_folder + os.sep + 'obsobs.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(obsobs)

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

        AR_res = y-yhat

        with open(Ass_folder + os.sep + 'residuals.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(AR_res)


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

        pct = count/float(len(rh))*100
        print('Percent out of bounds',pct)

        fig = matplotlib.pyplot.figure(figsize=(4.5, 3.5))

        matplotlib.rcParams.update({'font.size': 8, 'font.family': 'sans'})

        matplotlib.rc('ytick', labelsize=8)
        matplotlib.rc('xtick', labelsize=8)

        ylabel('Correlation coefficient')
        xlabel('Lag [days]')

        xlim([0,2500])

        plot(rh, linestyle = '-', marker = '.', markersize = 2)
        plot(ul, linestyle ='--', marker = 'None', color = 'black')
        plot(ll, linestyle ='--', marker = 'None', color = 'black')

##figname = 'C:\Users\Gudny\Thesis\Writing\Figures\Correlogram_Mokolo.pdf'
##savefig(figname)

        show()
