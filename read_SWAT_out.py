import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy
import datetime
import os
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from matplotlib.pylab import *
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()

def read_SWAT_out(src_folder,skiprows,outname):
    """Reads simulation results from SWAT daily output file."""
    filename = src_folder + os.sep + outname
    if os.path.isfile(filename):
        data = numpy.loadtxt(filename, skiprows=skiprows, converters={0: lambda s: 0})
        return(data)
    else:
        raise GeoAlgorithmExecutionException('File ' + filename + ' does not exist')


def reach_SWAT_ts(data,reachnr,varcol,variable):
    """Extracts reach and variable of interest from SWAT daily reach output"""
    if varcol == -1:
        raise GeoAlgorithmExecutionException('Variable ' + variable + ' not available in reach output')
    else:
        data_ex=data[data[:,1]==reachnr,varcol]
    if data_ex.size:
        return(data_ex)
    else:
        raise GeoAlgorithmExecutionException('Reach ' + str(reachnr) + ' does not exist in the model')


def sub_SWAT_ts(data,subnr,varcol, variable):
    """Extracts sub-basin and variable of interest from SWAT daily sub-basin output"""
    if varcol == -1:
        raise GeoAlgorithmExecutionException('Variable ' + variable + ' not available in sub-basin output')
    else:
        data_ex=data[data[:,1]==subnr,varcol]
    if data_ex.size:
        return(data_ex)
    else:
        raise GeoAlgorithmExecutionException('Sub-basin ' + str(subnr) + ' does not exist in the model')


def hru_SWAT_ts(data,subnr,hrunr,varcol, variable):
    """Extracts hru and variable of interest from SWAT daily hru output"""
    if varcol == -1:
        raise GeoAlgorithmExecutionException('Variable ' + variable + ' not available in hru output')
    else:
		data_ex=data[numpy.logical_and(data[:,3]==subnr, data[:,2]-data[:,3]*1e7==hrunr),varcol]
##        data_ex=data[numpy.logical_and(data[:,2]==subnr, data[:,3]==hrunr),varcol]
    if data_ex.size:
        return(data_ex)
    else:
        raise GeoAlgorithmExecutionException('Either sub-basin ' + str(subnr) + ' does not exist in the model or HRU ' +
                str(hrunr) + ' does not exist in sub-basin ' + str(subnr))

def rsv_SWAT_ts(src_folder,data,subnr,varcol,variable):
    """Extracts rsv and variable of interest from SWAT daily rsv output"""
    if varcol == -1:
        raise GeoAlgorithmExecutionException('Variable ' + variable + ' not available in rsv output')
    else:
		rsvnr = get_rsvnr(src_folder)
		data_ex=data[data[:,1]==rsvnr[subnr][0],varcol]
    if data_ex.size:
        return(data_ex, rsvnr)
    else:
        raise GeoAlgorithmExecutionException('Sub-basin ' + str(subnr) + ' does not contain a reservoir in the model')
		
def get_rsvnr(src_folder):
    filename = src_folder + os.sep + 'fig.fig'
    watershed_file = open(filename,'r').readlines()
    rsvnr = {}
    for l in watershed_file:
        try:
            if int(l[11:16]) == 3:  #Identify routres commands
                resID = int(l[23:28])
            if l[19:23] == '.res':
                rsvnr[int(l[0:15])] = [resID]
        except:
            pass
    return rsvnr		
				
def read_SWAT_time(src_folder):
    """Reads simulation timing from SWAT cio file"""
    filename = src_folder + os.sep + 'file.cio'
    if os.path.isfile(filename):
        data = numpy.zeros(5)
        cio_file = open(filename,'r')
        cio = cio_file.readlines()
        cio_file.close
        data[0]=int(cio[7][0:16])
        data[1]=int(cio[8][0:16])
        data[2]=int(cio[9][0:16])
        data[3]=int(cio[10][0:16])
        data[4]=int(cio[59][0:16])
        SWAT_time_info = data
        return(SWAT_time_info)
    else:
        raise GeoAlgorithmExecutionException('cio-file ' + filename + ' not available')

def reach_tsplot(SWAT_time_info,data,reachnr,variable,unit,folder,dateoffset,obsfile,TEMP_RES):
    """Produces a time series plot of a SWAT reach output variable"""
    if TEMP_RES == 0:
        # Daily resolution
        startyr = datetime.date(int(SWAT_time_info[1]),1,1)
        startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
        if SWAT_time_info[4] > 0:
            startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
        dates = [startdate + datetime.timedelta(days=i) for i in range(0,len(data))]
##        fig = plt.figure()
        plt.title(variable+' in reach '+str(reachnr), fontsize=12)
        plt.ylabel(variable + ' ($' + unit + '$)')
##        plt.plot_date(dates, data, linestyle='-',marker = 'None')
        plt.plot(dates, data, linestyle='-',marker = 'None')
        if os.path.isfile(obsfile):
            obsdata =  numpy.genfromtxt(obsfile, delimiter = ',', skiprows=0, missing_values = 'NaN')
            obsdata[:,0] = obsdata[:,0] + dateoffset
            plt.plot_date(obsdata[:,0], obsdata[:,1], ls='-', lw=0.5, marker = '.',markersize=4, color='r')
            plt.legend(['Model results','Observations'], fontsize=10, loc=2)
            # Calculate performance statistics: RMSE, ME, NSE
            obstimes = obsdata[:,0]
            obstimes = obstimes[~numpy.isnan(obsdata[:,1])]
            obs = obsdata[~numpy.isnan(obsdata[:,1]),1]
            nobs = len(obstimes)
            simobs = numpy.zeros(nobs)
            numdates = matplotlib.dates.date2num(dates)
            for i in range(0,nobs):
                extractsim=data[numdates==obstimes[i]]
                if len(extractsim) == 1:
                    simobs[i] = extractsim
                else:
                    simobs[i] = numpy.nan
            obs = obs[~numpy.isnan(simobs)]
            simobs = simobs[~numpy.isnan(simobs)]
            nobs = len(obs)
            meanobs = obs.mean()
            errorsimobs = simobs-obs
            meanerror = errorsimobs.mean()
            meanerrorpercent = meanerror/meanobs* 100
            varobs = obs - meanobs
            rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
            rmsepercent = rmse/meanobs*100
            nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
            statname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + 'performance_stats_daily.txt'
            statfile = open(statname,'w')
            statfile.writelines('Number of simulated observations: ' + str(nobs) + '\r\n')
            statfile.writelines('Mean of observations: ' + "%10.2f"% meanobs + ' ' + unit +'\r\n')
            statfile.writelines('Mean error (simulated - observed): ' + "%10.2f"% meanerror + ' ' + unit +
                ' (equivalent to ' + "%5.2f"% meanerrorpercent + ' percent of mean of observations)\r\n')
            statfile.writelines('Root mean squared error: ' + "%10.2f"% rmse + ' ' + unit +
                ' (equivalent to ' + "%5.2f"% rmsepercent + ' percent of mean of observations)\r\n')
            statfile.writelines('Nash-Sutcliffe model efficiency: ' + "%10.2f"% nse)
            statfile.close()
        figname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + '_daily.pdf'
        plt.savefig(figname)
        savenum = numpy.zeros((len(data),2))
        savenum[:,0]=matplotlib.dates.date2num(dates) - dateoffset
        savenum[:,1]=data
        csvname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + '_daily.csv'
        numpy.savetxt(csvname,savenum,delimiter=',')
        plt.show()
    elif TEMP_RES ==1:
        # Weekly resolution
        startyr = datetime.date(int(SWAT_time_info[1]),1,1)
        startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
        if SWAT_time_info[4] > 0:
            startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
        dates = [startdate + datetime.timedelta(days=i) for i in range(0,len(data))]
         # Compute weekly values
        data_weekly = []
        dates_plot = []
        for i in range(0,len(data)/7):
            data_weekly.append(numpy.mean(data[i*7:(i+1)*7]))
            dates_plot.append(dates[i*7])
        data_weekly = numpy.array(data_weekly)
        dates_plot = numpy.array(dates_plot)
        fig = plt.figure()
        plt.title(variable+' in reach '+str(reachnr), fontsize=12)
        plt.ylabel(variable + ' ($' + unit + '$)')
        plt.plot(dates_plot, data_weekly, linestyle='-',marker = 'None')
        if os.path.isfile(obsfile):
            obsdata =  numpy.genfromtxt(obsfile, delimiter = ',', skiprows=0, missing_values = 'NaN')
            obsdata[:,0] = obsdata[:,0] + dateoffset
            # Identify days with corresponding data
            obstimes = obsdata[:,0]
            nobs = len(obstimes)
            simobs = numpy.zeros(nobs)
            numdates = matplotlib.dates.date2num(dates)
            for i in range(0,nobs):
                extractsim=data[numdates==obstimes[i]]
                if len(extractsim) == 1:
                    simobs[i] = extractsim
                else:
                    simobs[i] = numpy.nan
            # Compute weekly values
            obsdata_weekly = []
            obsdates_plot = []
            simobs_weekly = []
            for i in range(0,nobs/7):
                if numpy.sum(numpy.isnan(obsdata[i*7:(i+1)*7,1])) > 2:
                    obsdata_weekly.append(numpy.nan)
                    obsdates_plot.append(obsdata[i*7,0])
                else:
                    obsdata_weekly.append(numpy.mean(numpy.ma.masked_array(obsdata[i*7:(i+1)*7,1],numpy.isnan(obsdata[i*7:(i+1)*7,1]))))
                    obsdates_plot.append(obsdata[i*7,0])
                if numpy.sum(numpy.isnan(simobs[i*7:(i+1)*7])) > 2:
                    simobs_weekly.append(numpy.nan)
                else:
                    simobs_weekly.append(numpy.mean(numpy.ma.masked_array(simobs[i*7:(i+1)*7],numpy.isnan(simobs[i*7:(i+1)*7]))))
            simobs_weekly = numpy.array(simobs_weekly)
            obsdata_weekly = numpy.array(obsdata_weekly)
            obsdates_plot = numpy.array(obsdates_plot)
            # Removing weeks without data
            obs = obsdata_weekly[~numpy.isnan(obsdata_weekly)]
            simobs = simobs_weekly[~numpy.isnan(obsdata_weekly)]
            simobs = simobs[~numpy.isnan(simobs)]
            obs = obs[~numpy.isnan(simobs)]
            obsdates_plot = obsdates_plot[~numpy.isnan(simobs)]
            # Calculate performance statistics: RMSE, ME, NSE
            meanobs = obs.mean()
            errorsimobs = simobs-obs
            meanerror = errorsimobs.mean()
            meanerrorpercent = meanerror/meanobs* 100
            varobs = obs - meanobs
            rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
            rmsepercent = rmse/meanobs*100
            nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
            statname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + 'performance_stats_weekly.txt'
            statfile = open(statname,'w')
            statfile.writelines('Number of simulated observations: ' + str(len(obs)) + '\r\n')
            statfile.writelines('Mean of observations: ' + "%10.2f"% meanobs + ' ' + unit +'\r\n')
            statfile.writelines('Mean error (simulated - observed): ' + "%10.2f"% meanerror + ' ' + unit +
                ' (equivalent to ' + "%5.2f"% meanerrorpercent + ' percent of mean of observations)\r\n')
            statfile.writelines('Root mean squared error: ' + "%10.2f"% rmse + ' ' + unit +
                ' (equivalent to ' + "%5.2f"% rmsepercent + ' percent of mean of observations)\r\n')
            statfile.writelines('Nash-Sutcliffe model efficiency: ' + "%10.2f"% nse)
            statfile.close()
            # Plotting
##            plt.plot_date(obsdates_plot, simobs, linestyle='-',marker = 'None')
            plt.plot_date(obsdates_plot, obs, linestyle='none',marker = '.',color='r')
            plt.legend(['Model results','Observations'])
        figname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + '_weekly.pdf'
        plt.savefig(figname)
        savenum = numpy.zeros((len(simobs),3))
        savenum[:,0]=obsdates_plot - dateoffset
        savenum[:,1]=simobs
        savenum[:,2]=obs
        csvname = folder + os.sep + 'Results_reach' + str(reachnr) + '_' + variable + '_weekly.csv'
        numpy.savetxt(csvname,savenum,delimiter=',')
        plt.show()

def sub_tsplot(SWAT_time_info,data,subnr,variable,unit,folder,dateoffset,obsfile):
    """Produces a time series plot of a SWAT sub-basin output variable"""
    startyr = datetime.date(int(SWAT_time_info[1]),1,1)
    startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
    if SWAT_time_info[4] > 0:
        startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
    dates = [startdate + datetime.timedelta(days=i) for i in range(0,len(data))]
    plt.title(variable+' in sub-basin '+str(subnr), fontsize=12)
    plt.ylabel(variable + ' ($' + unit + '$)')
    plt.plot(dates, data, linestyle='-',marker = 'None')
    if os.path.isfile(obsfile):
        obsdata =  numpy.genfromtxt(obsfile, delimiter = ',', skiprows=0, missing_values = 'NaN')
        obsdata[:,0] = obsdata[:,0] + dateoffset
        plt.plot(obsdata[:,0], obsdata[:,1], linestyle='none',marker = '.',color='r')
        plt.legend(['Model results','Observations'])
        # Calculate performance statistics: RMSE, ME, NSE
        obstimes = obsdata[:,0]
        obstimes = obstimes[~numpy.isnan(obsdata[:,1])]
        obs = obsdata[~numpy.isnan(obsdata[:,1]),1]
        nobs = len(obstimes)
        simobs = numpy.zeros(nobs)
        numdates = matplotlib.dates.date2num(dates)
        for i in range(0,nobs):
            extractsim=data[numdates==obstimes[i]]
            if len(extractsim) == 1:
                simobs[i] = extractsim
            else:
                simobs[i] = numpy.nan
        meanobs = obs.mean()
        errorsimobs = simobs-obs
        meanerror = errorsimobs.mean()
        meanerrorpercent = meanerror/meanobs * 100
        varobs = obs - meanobs
        rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
        rmsepercent = rmse/meanobs*100
        nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
        statname = folder + os.sep + 'Results_sub' + str(subnr) + '_' + variable + 'performance_stats.txt'
        statfile = open(statname,'w')
        statfile.writelines('Number of simulated observations: ' + str(nobs) + '\n')
        statfile.writelines('Mean of observations: ' + "%10.2f"% meanobs + ' ' + unit +'\n')
        statfile.writelines('Mean error (simulated - observed): ' + "%10.2f"% meanerror + ' ' + unit +
            ' (equivalent to ' + "%5.2f"% meanerrorpercent + ' percent of mean of observations)\n')
        statfile.writelines('Root mean squared error: ' + "%10.2f"% rmse + ' ' + unit +
            ' (equivalent to ' + "%5.2f"% rmsepercent + ' percent of mean of observations)\n')
        statfile.writelines('Nash-Sutcliffe model efficiency: ' + "%10.2f"% nse)
        statfile.close()
    figname = folder + os.sep + 'Results_sub' + str(subnr) + '_' + variable + '.pdf'
    plt.savefig(figname)
    savenum = numpy.zeros((len(data),2))
    savenum[:,0]=matplotlib.dates.date2num(dates) - dateoffset
    savenum[:,1]=data
    csvname = folder + os.sep + 'Results_sub' + str(subnr) + '_' + variable + '.csv'
    numpy.savetxt(csvname,savenum,delimiter=',')
    plt.show()

def hru_tsplot(SWAT_time_info,data,subnr,hrunr,variable,unit,folder,dateoffset,obsfile):
    """Produces a time series plot of a SWAT hru output variable"""
    startyr = datetime.date(int(SWAT_time_info[1]),1,1)
    startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
    if SWAT_time_info[4] > 0:
        startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
    dates = [startdate + datetime.timedelta(days=i) for i in range(0,len(data))]
    plt.title(variable+' in sub-basin '+str(subnr) + ' and hru ' + str(hrunr), fontsize=12)
    plt.ylabel(variable + ' ($' + unit + '$)')
    plt.plot(dates, data, linestyle='-',marker = 'None')
    if os.path.isfile(obsfile):
        obsdata =  numpy.genfromtxt(obsfile, delimiter = ',', skiprows=0, missing_values = 'NaN')
        obsdata[:,0] = obsdata[:,0] + dateoffset
        plt.plot(obsdata[:,0], obsdata[:,1], linestyle='none',marker = '.',color='r')
        plt.legend(['Model results','Observations'])
        # Calculate performance statistics: RMSE, ME, NSE
        obstimes = obsdata[:,0]
        obstimes = obstimes[~numpy.isnan(obsdata[:,1])]
        obs = obsdata[~numpy.isnan(obsdata[:,1]),1]
        nobs = len(obstimes)
        simobs = numpy.zeros(nobs)
        numdates = matplotlib.dates.date2num(dates)
        for i in range(0,nobs):
            extractsim=data[numdates==obstimes[i]]
            if len(extractsim) == 1:
                simobs[i] = extractsim
            else:
                simobs[i] = numpy.nan
        meanobs = obs.mean()
        errorsimobs = simobs-obs
        meanerror = errorsimobs.mean()
        meanerrorpercent = meanerror/meanobs * 100
        varobs = obs - meanobs
        rmse = numpy.sqrt(numpy.power(errorsimobs,2).mean())
        rmsepercent = rmse/meanobs*100
        nse = 1 - numpy.power(errorsimobs,2).sum()/numpy.power(varobs,2).sum()
        statname = folder + os.sep + 'Results_sub' + str(subnr) + '_hru' + str(hrunr) + '_' + variable + 'performance_stats.txt'
        statfile = open(statname,'w')
        statfile.writelines('Number of simulated observations: ' + str(nobs) + '\n')
        statfile.writelines('Mean of observations: ' + "%10.2f"% meanobs + ' ' + unit +'\n')
        statfile.writelines('Mean error (simulated - observed): ' + "%10.2f"% meanerror + ' ' + unit +
            ' (equivalent to ' + "%5.2f"% meanerrorpercent + ' percent of mean of observations)\n')
        statfile.writelines('Root mean squared error: ' + "%10.2f"% rmse + ' ' + unit +
            ' (equivalent to ' + "%5.2f"% rmsepercent + ' percent of mean of observations)\n')
        statfile.writelines('Nash-Sutcliffe model efficiency: ' + "%10.2f"% nse)
        statfile.close()
    figname = folder + os.sep + 'Results_sub' + str(subnr) + '_hru' +str(hrunr) + '_' + variable + '.pdf'
    plt.savefig(figname)
    savenum = numpy.zeros((len(data),2))
    savenum[:,0]=matplotlib.dates.date2num(dates) - dateoffset
    savenum[:,1]=data
    csvname = folder + os.sep + 'Results_sub' + str(subnr) + '_hru' + str(hrunr) + '_' + variable + '.csv'
    numpy.savetxt(csvname,savenum,delimiter=',')
    plt.show()
	
def rsv_tsplot(SWAT_time_info,data,subnr,rsvnr,variable,unit,folder,dateoffset,obsfile):
    """Produces a time series plot of a SWAT rsv output variable"""
    startyr = datetime.date(int(SWAT_time_info[1]),1,1)
    startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
    if SWAT_time_info[4] > 0:
        startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
    dates = [startdate + datetime.timedelta(days=i) for i in range(0,len(data))]
    plt.title(variable+' for reservoir in sub-basin '+str(subnr), fontsize=12)
    plt.ylabel(variable + ' ($' + unit + '$)')
    plt.plot(dates, data, linestyle='-',marker = 'None')
    figname = folder + os.sep + 'Results_sub' + str(subnr) + '_rsv' +str(rsvnr[subnr][0]) + '_' + variable + '.pdf'
    plt.savefig(figname)
    savenum = numpy.zeros((len(data),2))
    savenum[:,0]=matplotlib.dates.date2num(dates) - dateoffset
    savenum[:,1]=data
    csvname = folder + os.sep + 'Results_sub' + str(subnr) + '_rsv' + str(rsvnr[subnr][0]) + '_' + variable + '.csv'
    numpy.savetxt(csvname,savenum,delimiter=',')
    plt.show()	