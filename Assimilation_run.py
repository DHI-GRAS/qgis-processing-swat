#-------------------------------------------------------------------------------
# Name:        Assimilation_run
# Purpose:     Runs the assimilation scheme for a number of issue dates
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
import shutil
from datetime import date, timedelta
import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.pylab import *
from matplotlib import pyplot as plt
import subprocess
from PyQt4 import QtGui
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadNoSubs
import ASS_module3_Assimilation_ol
import ASS_module1_PrepData
import ASS_module2_ErrorModel_ol
import ASS_module4_Results_ol
from ASS_utilities import ReadObsFlowsAss
import ASS_Evaluation_ol

SRC_FOLDER = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\TxtInOut' #SWAT output folder
ASS_FOLDER = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\F_AssFolder'#storage location for assimilation input
OBS_FILE = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations
OBS_FILE_EM = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Kavango_Showcase_new\\In-situ_discharge\\Rundu.csv' #file with in-situ observations used for estimating the error model
#OBS_FILE_EM = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Calibration\\Rundu_cal.csv'
ERR_MOD_FILE = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\AssFolder_calval_abs\\ErrorModelReach10.txt' #name of the error model file
estimateem = False
writefiles = False
NBRCH = 12 #number of reaches in the model
REACH_ID = 10 #reach for which in-situ data is available

OUTSPECS = SWAT_output_format_specs()

# Get startdate and enddate from SWAT file.cio
SWAT_time_info = read_SWAT_time(SRC_FOLDER)
SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
if SWAT_time_info[4] > 0: # Account for NYSKIP>0
    SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1
header = OUTSPECS.REACH_SKIPROWS

# Prepare input txt files for assimilation
if writefiles:
    ASS_module1_PrepData.CreateTextFiles(NBRCH, SRC_FOLDER, ASS_FOLDER, header, SWAT_startdate, SWAT_enddate)

# Estimate error model
if estimateem:
    ASS_module2_ErrorModel.ErrorModel_discharge(OBS_FILE_EM, ASS_FOLDER, NBRCH, SWAT_enddate, SWAT_startdate)

# Copy error model parameters into assimilation input file
if writefiles:
    filename = ASS_FOLDER + os.sep + 'Assimilationfile.txt'
    if os.path.isfile(filename) & os.path.isfile(ERR_MOD_FILE):
        ass_lines = open(filename,'r').readlines()
        err_lines = open(ERR_MOD_FILE,'r').readlines()
        with open(ASS_FOLDER + os.sep + 'Assimilationfile.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(['Reach'] + ['X'] +  ['K']  + ['DrainsTo'] + ['Runoff'] +['alphaerr'] + ['Loss_fraction'])
            for j in range(0,NBRCH):
                l = ass_lines[j+1].split()
                file_writer.writerow([l[i] for i in range(0,5)]+[err_lines[1].split()[0]] + [l[6]])
        with open(ASS_FOLDER + os.sep + 'Assimilationfile_q.txt', 'wb') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=' ')
            file_writer.writerow(['q'])
            q = numpy.identity(NBRCH)*float(err_lines[1].split()[1])
            for k in range(0,NBRCH):
                file_writer.writerow(q[k])

# Run the assimilation
ASS_startdate = SWAT_startdate
ASS_enddate = SWAT_enddate

# Loop through all days in the validation period
today = date.today()
period = today-date(2007,4,12) + timedelta(1)
enddays = period.days
for i in range(0,5,1):
#    print(i)
    Issue_Date = date(2014,8,22) + datetime.timedelta(i)
    if os.path.isfile(OBS_FILE):
        Q_obs = ReadObsFlowsAss(OBS_FILE)
        Q_obs = Q_obs[find(numpy.isnan(Q_obs[:,1])==0),:]
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        if sum(Q_obs[:,0] >= ASS_startdate) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] >= ASS_startdate),:]
        if sum(Q_obs[:,0] <= date2num(Issue_Date)) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] <= date2num(Issue_Date)),:]
        obstoday = find(Q_obs[:,0] == date2num(Issue_Date))
        obstoday = size(obstoday)
    if obstoday > 0:
        Ass_Out_Folder = 'p:\\ACTIVE\\TigerNET 30966 PBAU\\Kavango\\Assimilation\\F_Ass_Out_' + str(Issue_Date) #set the assimilation output folder for each day
        if not(os.path.isdir(Ass_Out_Folder)):
            os.mkdir(Ass_Out_Folder)
        # Run the assimilation
        ASS_module3_Assimilation_ol.kf_flows(OBS_FILE, Q_obs, ASS_FOLDER, Ass_Out_Folder, NBRCH, ASS_enddate, ASS_startdate, date2num(Issue_Date), SWAT_enddate, SWAT_startdate)
        # Plot results
        ASS_module4_Results_ol.Results(OBS_FILE, str(Issue_Date), ASS_startdate, ASS_enddate, Ass_Out_Folder, REACH_ID)
        # Compute performance statistics
        ASS_Evaluation_ol.Results(ASS_startdate,ASS_enddate, Ass_Out_Folder, NBRCH, REACH_ID, Q_obs)

