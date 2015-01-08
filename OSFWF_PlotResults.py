"""
***************************************************************************
   OSFWF_PlotResults.py
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
from PyQt4 import QtGui
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
from datetime import date, timedelta, datetime
from read_SWAT_out import read_SWAT_time
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.pylab import *
import ASS_module4_Results
import ASS_module4_Results_weekly

class OSFWF_PlotResults(SWATAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    ASS_MODE = "ASS_MODE"
    ASS_FOLDER = "ASS_FOLDER"
    STARTDATE = "STARTDATE"
    OBSFILE = "OBSFILE"
    REACH_ID = "REACH_ID"

    def __init__(self):
        super(OSFWF_PlotResults, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "5 - Plot results (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_PlotResults.ASS_FOLDER, "Select assimilation folder", True))
        self.addParameter(ParameterFile(OSFWF_PlotResults.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterString(OSFWF_PlotResults.STARTDATE, "Issue date (yyyy-mm-dd)", str(date.today())))
        self.addParameter(ParameterFile(OSFWF_PlotResults.OBSFILE, "Select file with corresponding observations",False))
        self.addParameter(ParameterNumber(OSFWF_PlotResults.REACH_ID, "Reach ID", 1, 500, 1))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(OSFWF_PlotResults.SRC_FOLDER)
        ASS_MODE = self.getParameterValue(OSFWF_PlotResults.ASS_MODE)
        ASS_FOLDER = self.getParameterValue(OSFWF_PlotResults.ASS_FOLDER)
        STARTDATE = self.getParameterValue(OSFWF_PlotResults.STARTDATE)
        OBSFILE = self.getParameterValue(OSFWF_PlotResults.OBSFILE)
        REACH_ID = self.getParameterValue(OSFWF_PlotResults.REACH_ID)

        SWAT_time_info = read_SWAT_time(SRC_FOLDER)
        SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
        if SWAT_time_info[4] > 0: # Account for NYSKIP>0
            SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
        SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1

        # Assimilation startdate is 30 days prior to STARTDATE
        ASS_startdate = SWAT_startdate
        # Assimilation enddate is 8 days after STARTDATE
        ASS_enddate = SWAT_enddate
        ASS_module4_Results.Results(OBSFILE, str(STARTDATE), ASS_startdate, ASS_enddate, ASS_FOLDER, REACH_ID)
#        ASS_module4_Results.Results(OBSFILE, STARTDATE, ASS_startdate, ASS_enddate, ASS_FOLDER, REACH_ID)
