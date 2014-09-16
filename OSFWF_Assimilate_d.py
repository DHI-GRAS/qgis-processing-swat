"""
***************************************************************************
   OSFWF_Assimilate_d.py
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
from datetime import date, timedelta
from matplotlib.pylab import *
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterString import ParameterString
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadNoSubs
import ASS_module3_Assimilation

OUTSPECS = SWAT_output_format_specs()

class OSFWF_Assimilate_d(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    MOD_DESC = "MOD_DESC"
    ASS_FOLDER = "ASS_FOLDER"
    STARTDATE = "STARTDATE"
    OBS_FILE = "OBS_FILE"

    def defineCharacteristics(self):
        self.name = "4.4 - Assimilate observations (OSFWF) - run assimilation"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_Assimilate_d.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(OSFWF_Assimilate_d.MOD_DESC, "Select model description file", False, False))
        self.addParameter(ParameterFile(OSFWF_Assimilate_d.ASS_FOLDER, "Select assimilation folder", True))
        self.addParameter(ParameterString(OSFWF_Assimilate_d.STARTDATE, "Issue date (yyyy-mm-dd)", str(date.today())))
        self.addParameter(ParameterFile(OSFWF_Assimilate_d.OBS_FILE, "File with observation data (date, obs, measurement error, reach ID)", False))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(OSFWF_Assimilate_d.SRC_FOLDER)
        MOD_DESC = self.getParameterValue(OSFWF_Assimilate_d.MOD_DESC)
        ASS_FOLDER = self.getParameterValue(OSFWF_Assimilate_d.ASS_FOLDER)
        STARTDATE = self.getParameterValue(OSFWF_Assimilate_d.STARTDATE)
        OBS_FILE = self.getParameterValue(OSFWF_Assimilate_d.OBS_FILE)

        # Extract total number of subbasins from model description file
        NBRCH = ReadNoSubs(MOD_DESC)

        # Get startdate from SWAT file.cio
        SWAT_time_info = read_SWAT_time(SRC_FOLDER)
        SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
        if SWAT_time_info[4] > 0: # Account for NYSKIP>0
            SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
        SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1

        # Assimilation startdate is equal to SWAT start date
        ASS_startdate = SWAT_startdate
        # Assimilation enddate is equal to SWAT end date
        ASS_enddate = SWAT_enddate

        ASS_module3_Assimilation.kf_flows(OBS_FILE, ASS_FOLDER, NBRCH, ASS_enddate, ASS_startdate, SWAT_enddate, SWAT_startdate)

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
