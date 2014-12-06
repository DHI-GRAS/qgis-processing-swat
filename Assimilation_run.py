"""
***************************************************************************
   Assimilation_run.py
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

import os
import csv
import numpy
import shutil
from datetime import date, timedelta
import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.pylab import *
from matplotlib import pyplot as plt
import subprocess
from PyQt4 import QtGui
from SWAT_output_format_specs import SWAT_output_format_specs
import ASS_module3_Assimilation_ol
import ASS_module4_Results_ol
from ASS_utilities import ReadObsFlowsAss
import ASS_Evaluation_ol

# ################################################################################
# Remember hardwired spatial runoff correlation in ASS_module3_Assimilation_ol.py
# ################################################################################
ASS_FOLDER = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\Run_2_AssFolder'#storage location for assimilation input. If you want to change error model etc, change this
Check_Folder = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\Run_1\\F_Ass_Out_' #storage location for existing assimilation run (one per date) that should be copied
OBS_FILE = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations. If you want to change observation error, change this
ASS_OUT_FOLDER = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\Run_2\\Run_2_' # storage location for output, one folder per date
NBRCH = 12 #number of reaches in the model
REACH_ID = 10 #reach for which in-situ data is available
Sim_startdate = date(2005,1,1)
ASS_startdate = date(2012,1,1)
ASS_enddate = date(2014,12,2)
# ################################################################################
OUTSPECS = SWAT_output_format_specs()

# Run the assimilation
# Loop through all days in the requested period
period = ASS_enddate-ASS_startdate
enddays = period.days + 1
for i in range(0,enddays,1):
    Issue_Date = ASS_startdate + timedelta(i)
    print(str(Issue_Date))
    if os.path.isfile(OBS_FILE):
        Q_obs = ReadObsFlowsAss(OBS_FILE)
        Q_obs = Q_obs[find(numpy.isnan(Q_obs[:,1])==0),:]
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        if sum(Q_obs[:,0] >= date2num(Sim_startdate)) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] >= date2num(Sim_startdate)),:]
        if sum(Q_obs[:,0] <= date2num(Issue_Date)) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] <= date2num(Issue_Date)),:]
        obstoday = find(Q_obs[:,0] == date2num(Issue_Date))
        obstoday = size(obstoday)
    if obstoday > 0:
        Check_Folder_with_date = Check_Folder + str(Issue_Date) #set the assimilation output folder for each day
        ASS_OUT_FOLDER_with_date = ASS_OUT_FOLDER + str(Issue_Date) #set the assimilation output folder for each day
        if os.path.isdir(Check_Folder_with_date):
            if not(os.path.isdir(ASS_OUT_FOLDER_with_date)):
                os.mkdir(ASS_OUT_FOLDER_with_date)
                src_files = os.listdir(Check_Folder_with_date)
                for file_name in src_files:
                    if file_name.endswith('.txt'):
                        full_file_name = os.path.join(Check_Folder_with_date, file_name)
                        if (os.path.isfile(full_file_name)):
                            shutil.copy(full_file_name, ASS_OUT_FOLDER_with_date)
                shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile.txt",ASS_OUT_FOLDER_with_date + os.sep + "Assimilationfile.txt")
                shutil.copyfile(ASS_FOLDER + os.sep + "Assimilationfile_q.txt",ASS_OUT_FOLDER_with_date + os.sep + "Assimilationfile_q.txt")
        else:
            if not(os.path.isdir(ASS_OUT_FOLDER_with_date)):
                os.mkdir(ASS_OUT_FOLDER_with_date)
            src_files = os.listdir(ASS_FOLDER)
            for file_name in src_files:
                full_file_name = os.path.join(ASS_FOLDER, file_name)
                if (os.path.isfile(full_file_name)):
                    shutil.copy(full_file_name, ASS_OUT_FOLDER_with_date)
        filename = ASS_OUT_FOLDER_with_date + os.sep + 'runoff'+ str(1) + '.txt'
        # Check size of runoff forcing to set simulation end date
        RR = numpy.genfromtxt(filename, delimiter = ' ', skip_header = 1, usecols=1)
        numpy.size(RR)
        Sim_enddate = Sim_startdate + timedelta(numpy.size(RR)-1)
        # Run the assimilation
        ASS_module3_Assimilation_ol.kf_flows(Q_obs, ASS_OUT_FOLDER_with_date, NBRCH, date2num(Sim_enddate), date2num(Sim_startdate), date2num(Issue_Date), date2num(Sim_enddate), date2num(Sim_startdate))
        # Plot results
        ASS_module4_Results_ol.Results(OBS_FILE, str(Issue_Date), date2num(Sim_startdate), date2num(Sim_enddate), ASS_OUT_FOLDER_with_date, REACH_ID)
        # Compute performance statistics
        ASS_Evaluation_ol.Results(date2num(Sim_startdate), date2num(Sim_enddate), ASS_OUT_FOLDER_with_date, NBRCH, REACH_ID, Q_obs)

