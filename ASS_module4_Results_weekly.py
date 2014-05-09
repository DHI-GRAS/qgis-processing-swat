# Import modules
import matplotlib.pyplot as plt
import numpy
import os
import csv
from datetime import date, timedelta
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from ASS_utilities import ReadObsFlowsAss

def Results(obs_file, Startdate, Enddate, Ass_folder, nbrch):

    #Getting the observed data for the assimilation (assimilation starting date to issue day (Enddate-8))
    if os.path.isfile(obs_file):
        Q_obs = ReadObsFlowsAss(obs_file)
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        reachID = []
        reachID.append(Q_obs[0,3])
        for i in range(1,len(Q_obs)):
            if Q_obs[i,3] != reachID[-1]:
                reachID.append(Q_obs[i,3])
    else:
        raise GeoAlgorithmExecutionException('File ' + obsfile + ' does not exist')

    for n in range(0,len(reachID)):
        # Calculate weekly values
        Q_obs_weekly = numpy.zeros([numpy.size(Q_obs,0)/7,1], dtype=float)
        for i in range(0,numpy.size(Q_obs,0)/7):
            if numpy.mean(Q_obs[i*7:(i+1)*7,3]) == reachID[n]:
                if numpy.sum(numpy.isnan(Q_obs[i*7:(i+1)*7,1])) > 2:
                    Q_obs_weekly[i] = numpy.nan
                else:
                    Q_obs_weekly[i] = numpy.mean(numpy.ma.masked_array(Q_obs[i*7:(i+1)*7,1],numpy.isnan(Q_obs[i*7:(i+1)*7,1])))

        mean_obs_weekly = numpy.mean(numpy.ma.masked_array(Q_obs_weekly,numpy.isnan(Q_obs_weekly)))

        #Routed simulation data
        x3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Output.csv', delimiter=',')
        P3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Cov.csv', delimiter=',')
        q_ass = x3[int(reachID[n])-1,:]
        std_ass = P3[int(reachID[n])-1,:]

        #Creating the bounds
        up_bound_ass = q_ass+2*std_ass
        low_bound_ass = numpy.zeros([len(q_ass)])
        for j in range (0,len(q_ass)):
            if q_ass[j]-2*std_ass[j]>0:
                low_bound_ass[j] = q_ass[j]-2*std_ass[j]
            else:
                low_bound_ass[j] = 0

        timestep = (Enddate-Startdate+1)/len(q_ass)

        #Preparing the simulated flows
        sim_ass_daily = q_ass

        q_ass_weekly = []
        for i in range(1,len(q_ass)/7):
            q_ass_weekly.append(mean(q_ass[(i-1)*7+1:i*7]))

        #Excluding nan flows
        obs_weekly = array(Q_obs_weekly)
        obs_weekly[find(numpy.isnan(Q_obs_weekly))] = -1

        a = numpy.where(obs_weekly>0)
        obs_det_sum = 0
        obs_ass_sum = 0
        for i in range(0,len(a[0])):
            obs_det_sum = obs_det_sum + ((sim_det_weekly[a[0][i]]-obs_weekly[a[0][i]])**2)
            obs_ass_sum = obs_ass_sum + ((sim_ass_weekly[a[0][i]]-obs_weekly[a[0][i]])**2)

        # Create plot
        xsim = numpy.arange(1,len(q_ass_weekly))
        xobs = numpy.arange(1,len(Q_obs_weekly))
        fig = plt.figure()
        plt.title('Assimilation results for reach  '+str(int(reachID[n])), fontsize=12)
        plt.ylabel('Discharge [$m^3/s$]')
        p1, = plt.plot_date(xsim, q_ass_weekly, linestyle='-',color='green', marker = 'None')
        plt.plot_date(xsim, low_bound_ass, linestyle='--', color = 'green',marker = 'None')
        plt.plot_date(xsim, up_bound_ass, linestyle='--', color = 'green',marker = 'None')
        p2, = plt.plot_date(xobs, Q_obs_weekly, color='red', marker = '.')
        plt.legend([p1,p2],['Assimilated Run','Observed'])
        plt.legend(loc=0)
        grid(True)
        grid(True)
        ax1 = fig.add_subplot(111)
        ax1.fill_between(xsim, low_bound_ass, up_bound_ass, color='green',alpha=.3)
        p = []
        for i in range(-30,9):
            p.append(str(i))
        p[30]= str(num2date(Enddate-8))[0:10]
        plt.xticks(numpy.arange(dates[0],dates[-1]+1), p, size='xx-small')
        plt.xlim([Startdate+20, Enddate])
        figname = Ass_folder + os.sep + 'Assimilation_Results_reach' + str(int(reachID[n])) + '.pdf'
        plt.savefig(figname)
        plt.show()

if __name__ == '__main__':
    Ass_folder = 'c:\\Research\\Assimilation\\TxtInOut_235\\Assimilation'            #Folder where results are stored
    src_folder = 'c:\\Research\\Assimilation\\TxtInOut_235'                           #Folder with SWAT results
    obs_file = 'c:\\Research\\Assimilation\\TxtInOut_235\\Rundu_error.csv'                   #Folder with observed discharge data
    nbrch = 7                                                                   #Total number of reaches

    #Get the startdate and endate from SWAT fil.cio and compare with startdate of data to determine header in output files
    deli = [10,7,8]
    Startdate = date2num(date(2005,2,15))
    Dates = genfromtxt(src_folder + os.sep + 'file.cio', skip_header = 7, delimiter = deli, usecols=1)
    Startdate_SWAT = date2num(date((int(Dates[1])-1),12,31))+Dates[2]
    Enddate = date2num(date(int(Dates[1]+Dates[0]-1),1,1))+Dates[3]
    NYSKIP = Dates[52]                              # number of years skipped in output printing/summarization
    if NYSKIP > 0:
        Startdate_SWAT_results = date2num(date((int(Dates[1]+NYSKIP)),1,1))
        header = int((Startdate-Startdate_SWAT_results)*nbrch+9)
    else:
        header = 9

    Results(obs_file, Startdate, Enddate, Ass_folder, nbrch)
