"""
***************************************************************************
   OSFWF_Assimilate_a.py
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
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadNoSubs
import ASS_module1_PrepData

OUTSPECS = SWAT_output_format_specs()

class OSFWF_Assimilate_a(SWATAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    MOD_DESC = "MOD_DESC"
    ASS_FOLDER = "ASS_FOLDER"
    
    def __init__(self):
        super(OSFWF_Assimilate_a, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "4.1 - Assimilate observations (OSFWF) - prepare input data"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.MOD_DESC, "Select model description file", False, False))
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.ASS_FOLDER, "Select assimilation folder", True))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(OSFWF_Assimilate_a.SRC_FOLDER)
        MOD_DESC = self.getParameterValue(OSFWF_Assimilate_a.MOD_DESC)
        ASS_FOLDER = self.getParameterValue(OSFWF_Assimilate_a.ASS_FOLDER)

        # Extract total number of subbasins from model description file
        NBRCH = ReadNoSubs(MOD_DESC)

        # Get startdate from SWAT file.cio and compare with startdate of assimilation to determine header in SWAT output files
        SWAT_time_info = read_SWAT_time(SRC_FOLDER)
        SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
        if SWAT_time_info[4] > 0: # Account for NYSKIP>0
            SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
        SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1
        header = OUTSPECS.REACH_SKIPROWS

        ASS_module1_PrepData.CreateTextFiles(NBRCH, SRC_FOLDER, ASS_FOLDER, header, SWAT_startdate, SWAT_enddate)

