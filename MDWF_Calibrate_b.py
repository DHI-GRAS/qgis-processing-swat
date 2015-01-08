"""
***************************************************************************
   MDWF_Calibrate_b.py
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
from datetime import date, timedelta, datetime
import numpy
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
import SWAT_PEST_utilities
from ASS_utilities import ReadNoSubs

class MDWF_Calibrate_b(SWATAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    MOD_DESC = "MOD_DESC"
    OBS_FILE = "OBS_FILE"
    OBS_GROUP = "OBS_GROUP"
##    SUB_ID = "SUB_ID"
    TEMP_RES = "TEMP_RES"

    def __init__(self):
        super(MDWF_Calibrate_b, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "5.2 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - generate instruction files"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Calibrate_b.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(MDWF_Calibrate_b.MOD_DESC, "Select model description file", False, False))
        self.addParameter(ParameterFile(MDWF_Calibrate_b.OBS_FILE, "File with observation data (time, obs, error, reach ID)", False, False))
        self.addParameter(ParameterString(MDWF_Calibrate_b.OBS_GROUP, "PEST name of observation group", 'discharge'))
##        self.addParameter(ParameterNumber(MDWF_Calibrate_b.SUB_ID, "Subbasin corresponding to observations", 1,500,1))
        self.addParameter(ParameterSelection(MDWF_Calibrate_b.TEMP_RES, "Temporal resolution of reach output and observation data", ['Daily','Monthly'], False))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(MDWF_Calibrate_b.SRC_FOLDER)
        MOD_DESC = self.getParameterValue(MDWF_Calibrate_b.MOD_DESC)
        OBS_FILE = self.getParameterValue(MDWF_Calibrate_b.OBS_FILE)
        OBS_GROUP = self.getParameterValue(MDWF_Calibrate_b.OBS_GROUP)
##        SUB_ID = self.getParameterValue(MDWF_Calibrate_b.SUB_ID)
        TEMP_RES = self.getParameterValue(MDWF_Calibrate_b.TEMP_RES)

        # Extract total number of subbasins from model description file
        N_SUBS = ReadNoSubs(MOD_DESC)

##        insname, obsblockname = SWAT_PEST_utilities.create_PEST_instruction(SRC_FOLDER, OBS_FILE, OBS_GROUP, SUB_ID, N_SUBS,TEMP_RES)
        insname, obsblockname = SWAT_PEST_utilities.create_PEST_instruction(SRC_FOLDER, OBS_FILE, OBS_GROUP, N_SUBS,TEMP_RES)

