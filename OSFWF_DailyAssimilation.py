import os
import csv
import numpy
import shutil
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
import ASS_Evaluation
from ASS_utilities import ReadObsFlowsAss
import GetGfsClimateData
from ModelFile import ModelFile
from ClimateStationsSWAT import ClimateStationsSWAT
from ZonalStats import ZonalStats
from datetime import date, timedelta, datetime
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException


class OSFWF_DailyAssimilation(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = "Daily Assimilation (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"

    def processAlgorithm(self, progress):
        progress.setConsoleInfo("Downloading new weather data...")
        SRC_FOLDER = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\TxtInOut' #SWAT output folder
        ASS_FOLDER = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\F_AssFolder'#storage location for assimilation input
        OBS_FILE = 'r:\\Projects\\TigerNET\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations
        pcp_folder = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\APCP'
        tmax_folder = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\TMAX'
        tmin_folder = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\TMIN'
        forecast_dates_file = "r:\\Projects\\TigerNET\\Kavango\\Assimilation\\Climate_stations\\ForecastDates.txt"
        logfilename = "r:\\Projects\\TigerNET\\Kavango\\Assimilation\\Climate_stations\\log.txt"
        climstatfilename = "r:\\Projects\\TigerNET\\Kavango\\Assimilation\\Climate_stations\KavangoStations.txt"
        subcatchmap_res = 0.01
        correct_factor = 0.67
        model = ModelFile("r:\\Projects\\TigerNET\\Kavango\\Kavango_Showcase_new\\ModelDescription.txt")
        NBRCH = 12 #number of reaches in the model
        REACH_ID = 10 #reach for which in-situ data is available
        OUTSPECS = SWAT_output_format_specs()
        SWAT_EXE = SRC_FOLDER + os.sep + "swat2009DtuEnv.exe"
        Issue_Date = date.today()
        Ass_Out_Folder = 'r:\\Projects\\TigerNET\\Kavango\\Assimilation\\F_Ass_Out_' + str(Issue_Date)

        # Download new NOAA GFS data
        for var in ['APCP','TMAX','TMIN']:
            # Set destination folder and level
            if var == 'APCP':
                dst_folder = pcp_folder
                level = 'surface'
            elif var == 'TMAX':
                dst_folder = tmax_folder
                level = '2_m_above_ground'
            elif var == 'TMIN':
                dst_folder = tmin_folder
                level = '2_m_above_ground'

            if os.path.isdir(dst_folder):
                # Create and set Forecast folder
                forecast_folder = dst_folder + os.sep + 'Forecasts'
                if not os.path.isdir(forecast_folder):
                    os.mkdir(forecast_folder)

                # Creating log file
                log_file = open(dst_folder + os.sep + "Download_log.txt", "w")
                # Write current date to log file
                now = date.today()
                log_file.write(' run: ' + now.strftime('%Y%m%d') + '\n')
                log_file.write('Data source: NOAA-GFS\n')

                # Finding newest file date and move old forecasted files to forecast folder
                dates = []
                dirs = os.listdir(dst_folder)
                for f in dirs:
                    if ( os.path.isfile(os.path.join(dst_folder,f)) ):
                        if (var + '.tif') in f:
                            dates.append(date(int(f[0:4]),int(f[4:6]),int(f[6:8])))
                        elif (var + '_Forecast_') in f:
                            shutil.copy(os.path.join(dst_folder,f),forecast_folder + os.sep + os.path.split(f)[1])
                            os.remove(os.path.join(dst_folder,f))

                # Newest file date +1 or today-60days (if no files) as start date
                if dates == []:
                    first_date = now - timedelta(days=60)
                else:
                    first_date = max(dates) + timedelta(days=1)
                    log_file.write(var + ' downloading start date: ' + first_date.strftime('%Y%m%d') + '\n')

                    # Downloading data
                    forecast_date = GetGfsClimateData.GfsForecastImport(first_date, var, level, dst_folder, -20, 55, 40, -40, log_file, progress)
                    log_file.write('Forecast date ' + var + ': ' + forecast_date.strftime('%Y%m%d') + '\n')

                    log_file.close()


        # Update Model climate data
        # Create log file
        log_file = open(logfilename, "w")
        # Write current date to log file
        now = date.today()
        log_file.write(self.name + ' run date: ' + now.strftime('%Y%m%d') + '\n')

        # Load SWAT stations file
        stations = ClimateStationsSWAT(climstatfilename)

        progress.setConsoleInfo("Reading old climate data...")
        # Getting SWAT .pcp data
        pcp_juliandates, first_pcp_date, last_pcp_date, pcp_array = stations.readSWATpcpFiles(log_file)
##        numpy.savetxt(model.Path + os.sep + 'pcp_array.csv', pcp_array, delimiter=",")
##        log_file.write(str(pcp_dates))

        # Getting SWAT .tmp data
        tmp_juliandates, first_tmp_date, last_tmp_date, tmp_max_array, tmp_min_array = stations.readSWATtmpFiles(log_file)
##        numpy.savetxt(model.Path + os.sep + 'tmp_max_array.csv', tmp_max_array, delimiter=",")

        # Delete last forecast in .pcp and .tmp data if Real Time model

        # Read last forecast dates from file
        forecast_dates = {}
        forecast_file=open(forecast_dates_file,'r').readlines()
        if not forecast_file[0].find('Forecast dates file') == -1:
            for line in range(1,len(forecast_file)):
                (key, val) = forecast_file[line].split()
                forecast_dates[key] = val

            # setting new last_dates and crop arrays
            # APCP
            new_last_pcp_date = datetime.strptime(forecast_dates['APCP'], "%Y%m%d").date() - timedelta(days=1)
            dif = (last_pcp_date - new_last_pcp_date).days
            if dif > 0:
                pcp_array = pcp_array[:-dif,:]
                pcp_juliandates = pcp_juliandates[:-dif]
                last_pcp_date = new_last_pcp_date
            # TMP
            new_last_tmp_date = datetime.strptime(forecast_dates['TMP'], "%Y%m%d").date() - timedelta(days=1)
            dif = (last_tmp_date - new_last_tmp_date).days
            if dif > 0:
                tmp_max_array = tmp_max_array[:-dif,:]
                tmp_min_array = tmp_min_array[:-dif,:]
                tmp_juliandates = tmp_juliandates[:-dif]
                last_tmp_date = new_last_tmp_date


        progress.setConsoleInfo("Searching for new files...")
        # Getting list of new pcp data files
        new_pcp_files = []
        new_pcp_enddate = last_pcp_date
        dirs = os.listdir(pcp_folder)
        pcp_forecast_var = 'APCP_Forecast_'
        pcp_var_GFS = 'APCP.tif'
        pcp_var_RFE = '_rain_.tif'
        for f in dirs:
            if (pcp_var_GFS in f) or (pcp_var_RFE in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_pcp_date < file_date):
                    new_pcp_files.append(pcp_folder + os.sep + f)
                    # Find the last date
                    if new_pcp_enddate < file_date:
                        new_pcp_enddate = file_date
            # Append forecast files for real-time
            elif (pcp_forecast_var in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_pcp_date < file_date):
                    new_pcp_files.append(pcp_folder + os.sep + f)
                    # Find the last date
                    if new_pcp_enddate < file_date:
                        new_pcp_enddate = file_date
                    new_pcp_forecast_date = f.split(pcp_forecast_var)[1].split('.tif')[0]

        # Getting list of new tmax data files
        new_tmax_files = []
        new_tmax_enddate = last_tmp_date
        tmax_var_GFS = 'TMAX.tif'
        tmax_var_ECMWF = '_TMAX_ECMWF.tif'
        tmax_forecast_var = 'TMAX_Forecast_'
        dirs = os.listdir(tmax_folder)
        for f in dirs:
            if (tmax_var_GFS in f) or (tmax_var_ECMWF in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_tmp_date < file_date):
                    new_tmax_files.append(tmax_folder + os.sep + f)
                    # Find the last date
                    if new_tmax_enddate < file_date:
                        new_tmax_enddate = file_date
            # Append forecast files for real-time
            elif (tmax_forecast_var in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_tmp_date < file_date):
                    new_tmax_files.append(tmax_folder + os.sep + f)
                    # Find the last date
                    if new_tmax_enddate < file_date:
                        new_tmax_enddate = file_date
                    new_tmax_forecast_date = f.split(tmax_forecast_var)[1].split('.tif')[0]

        # Getting list of new tmin data files
        new_tmin_files = []
        new_tmin_enddate = last_tmp_date
        tmin_var_GFS = 'TMIN.tif'
        tmin_var_ECMWF = '_TMIN_ECMWF.tif'
        tmin_forecast_var = 'TMIN_Forecast_'
        dirs = os.listdir(tmin_folder)
        for f in dirs:
            if (tmin_var_GFS in f) or (tmin_var_ECMWF in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_tmp_date < file_date):
                    new_tmin_files.append(tmin_folder + os.sep + f)
                    # Find the last date
                    if new_tmin_enddate < file_date:
                        new_tmin_enddate = file_date
            # Append forecast files for real-time
            elif (tmin_forecast_var in f):
                file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
                # Only get new files
                if (last_tmp_date < file_date):
                    new_tmin_files.append(tmin_folder + os.sep + f)
                    # Find the last date
                    if new_tmin_enddate < file_date:
                        new_tmin_enddate = file_date
                    new_tmin_forecast_date = f.split(tmin_forecast_var)[1].split('.tif')[0]

##        log_file.write('APCP files: ' + str(new_pcp_files) + '\n')
##        log_file.write('TMAX files: ' + str(new_tmax_files) + '\n')
##        log_file.write('TMIN files: ' + str(new_tmin_files) + '\n')

        progress.setConsoleInfo("Extracting precipitation data...")
        # Process new APCP files
        if not new_pcp_files == []:
            # Get new array
            pcp_startdate = last_pcp_date + timedelta(days=1)
            new_pcp_juliandates, new_pcp_array = ZonalStats(pcp_startdate, new_pcp_enddate, model.Path, \
                model.desc['ModelName'], model.Path+os.sep+model.desc['Shapefile'], model.desc['SubbasinColumn'], \
                subcatchmap_res, new_pcp_files, log_file, GeoAlgorithmExecutionException, None, correct_factor)
            # Combine arrays
            pcp_juliandates = numpy.concatenate((pcp_juliandates, new_pcp_juliandates), axis=0)
            pcp_array = numpy.concatenate((pcp_array, new_pcp_array), axis=0)
            progress.setConsoleInfo("Writing new precipitation files...")
            # Write files
            stations.writeSWATpcpFiles(pcp_juliandates, pcp_array, log_file)

        progress.setConsoleInfo("Extracting temperature data...")
        # Process Temperature files
        if not (new_tmax_files == [] and new_tmin_files == []):
            # Get new array
            # TMAX
            # Get corrections
            if tmax_var_ECMWF in new_tmax_files[0]:
                correct_number = -273.15
                pass
            else:
                correct_number = None
            tmp_startdate = last_tmp_date + timedelta(days=1)
            new_tmax_juliandates, new_tmp_max_array = ZonalStats(tmp_startdate, new_tmax_enddate, model.Path, \
                model.desc['ModelName'], model.Path+os.sep+model.desc['Shapefile'], model.desc['SubbasinColumn'], \
                subcatchmap_res, new_tmax_files, log_file, GeoAlgorithmExecutionException, correct_number, None)
            # TMIN
            if tmin_var_ECMWF in new_tmin_files[0]:
                correct_number = -273.15
                pass
            else:
                correct_number = None
            new_tmin_juliandates, new_tmp_min_array = ZonalStats(tmp_startdate, new_tmin_enddate, model.Path, \
                model.desc['ModelName'], model.Path+os.sep+model.desc['Shapefile'], model.desc['SubbasinColumn'], \
                subcatchmap_res, new_tmin_files, log_file, GeoAlgorithmExecutionException, correct_number, None)

            # Make shure tmax and tmin have same end days
            dif = (len(new_tmax_juliandates)-len(new_tmin_juliandates))
            if dif > 0:
                new_tmp_max_array = new_tmp_max_array[:-dif,:]
                new_tmax_juliandates = new_tmax_juliandates[:-dif]
                if model.desc['Type'] == 'RT':
                    new_tmp_forecast_date = new_tmin_forecast_date
            elif dif < 0:
                new_tmp_min_array = new_tmp_min_array[:-dif,:]
                new_tmin_juliandates = new_tmin_juliandates[:-dif,:]
                if model.desc['Type'] == 'RT':
                    new_tmp_forecast_date = new_tmax_forecast_date
            else:
                if model.desc['Type'] == 'RT':
                    new_tmp_forecast_date = new_tmax_forecast_date

            progress.setConsoleInfo("Writing new temperature files...")
            # Combine arrays
            # TMAX
            tmp_juliandates = numpy.concatenate((tmp_juliandates, new_tmax_juliandates), axis=0)
            tmp_max_array = numpy.concatenate((tmp_max_array, new_tmp_max_array), axis=0)
            # TMIN
            tmp_min_array = numpy.concatenate((tmp_min_array, new_tmp_min_array), axis=0)
            # Write files
            stations.writeSWATtmpFiles(tmp_juliandates, tmp_max_array, tmp_min_array, log_file)

            progress.setConsoleInfo("Update model files...")
            # Updating forecast file
            if model.desc['Type'] == 'RT':
                if new_pcp_files == []:
                    new_pcp_forecast_date = forecast_dates['APCP']
                forecast_file=open(forecast_dates_file,'w')
                forecast_file.write('Forecast dates file \n')
                forecast_file.write('APCP ' + new_pcp_forecast_date + '\n')
                forecast_file.write('TMP ' + new_tmp_forecast_date + '\n')

        log_file.close()

        # Run SWAT model
        # Updating climate files
        CSTATIONS = ClimateStationsSWAT(climstatfilename)
        log_file = open(SRC_FOLDER + os.sep + "cstations_log.txt", "w")
        last_pcp_date,last_tmp_date = CSTATIONS.writeSWATrunClimateFiles(SRC_FOLDER,log_file)
        log_file.close()

        # Updating cio file
        last_date = min(last_pcp_date,last_tmp_date)
        if os.path.isfile(SRC_FOLDER + os.sep + "file.cio"):
            cio_file = open(SRC_FOLDER + os.sep + "file.cio", "r")
            cio=cio_file.readlines()
            cio_file.close()
            startyear = int(cio[8][0:16])
            nbyears = last_date.year - startyear + 1
            endjulianday = (last_date-date(last_date.year,1,1)).days + 1
            nbyearline = str(nbyears).rjust(16) + cio[7][16:len(cio[7])]
            endjdayline = str(endjulianday).rjust(16) + cio[10][16:len(cio[10])]
            cio[7]=nbyearline
            cio[10]=endjdayline
            cio_file = open(SRC_FOLDER + os.sep + "file.cio", "w")
            cio_file.writelines(cio)
            cio_file.close()
        else:
            raise GeoAlgorithmExecutionException('cio-file ' + SRC_FOLDER + os.sep + "file.cio" + ' does not exist')

        # Running SWAT
        currpath = os.getcwd()
        os.chdir(SRC_FOLDER)
        runres = subprocess.call(SWAT_EXE)
        os.chdir(currpath)
        if runres != 0:
            raise GeoAlgorithmExecutionException('SWAT run unsuccessful')

        # Get startdate and enddate from SWAT file.cio
        SWAT_time_info = read_SWAT_time(SRC_FOLDER)
        SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
        if SWAT_time_info[4] > 0: # Account for NYSKIP>0
            SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
        SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1

        # Prepare runoff files only
        shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile.txt",ASS_FOLDER + os.sep + "Assimilationfile_f.txt")
        shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile_q.txt",ASS_FOLDER + os.sep + "Assimilationfile_q_f.txt")
        ASS_module1_PrepData.CreateTextFiles(NBRCH, SRC_FOLDER, ASS_FOLDER, OUTSPECS.REACH_SKIPROWS, SWAT_startdate, SWAT_enddate)
        shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile_f.txt",ASS_FOLDER + os.sep + "Assimilationfile.txt")
        shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile_q_f.txt",ASS_FOLDER + os.sep + "Assimilationfile_q.txt")
        os.remove(ASS_FOLDER + os.sep + "Assimilationfile_f.txt")
        os.remove(ASS_FOLDER + os.sep + "Assimilationfile_q_f.txt")

        # Run the assimilation
        ASS_startdate = SWAT_startdate
        ASS_enddate = SWAT_enddate
        if not(os.path.isdir(Ass_Out_Folder)):
            os.mkdir(Ass_Out_Folder)
        src_files = os.listdir(ASS_FOLDER)
        for file_name in src_files:
            full_file_name = os.path.join(ASS_FOLDER, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, Ass_Out_Folder)

        # Run the assimilation
        ASS_module3_Assimilation.kf_flows(OBS_FILE, Ass_Out_Folder, NBRCH, ASS_enddate, ASS_startdate, SWAT_enddate, SWAT_startdate)
        # Plot results
        ASS_module4_Results.Results(OBS_FILE, str(Issue_Date), ASS_startdate, ASS_enddate, Ass_Out_Folder, REACH_ID)
        # Compute performance statistics
        ASS_Evaluation.Results(ASS_startdate,ASS_enddate, Ass_Out_Folder, NBRCH, REACH_ID, OBS_FILE)

    def getIcon(self):
        return  QtGui.QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

    def helpFile(self):
        [folder, filename] = os.path.split(__file__)
        [filename, _] = os.path.splitext(filename)
        helpfile = str(folder) + os.sep + "doc" + os.sep + filename + ".html"
        if os.path.exists(helpfile):
            return helpfile
        else:
            raise WrongHelpFileException("Sorry, no help is available for this algorithm.")
