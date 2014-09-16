"""
***************************************************************************
   MDWF_Calibrate_a.py
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
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterString import ParameterString
from processing.parameters.ParameterSelection import ParameterSelection
import SWAT_PEST_utilities
from SWAT_parameter_specs import SWAT_parameter_specs

PARSPECS = SWAT_parameter_specs()

class MDWF_Calibrate_a(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    CAL_PAR = "CAL_PAR"
    PAR_NAME = "PAR_NAME"
    SUB_ID = "SUB_ID"
    HRU_ID = "HRU_ID"
    PARVAL1 = "PARVAL1"
    PARLBND = "PARLBND"
    PARUBND = "PARUBND"


    def defineCharacteristics(self):
        self.name = "5.1 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - generate template files"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Calibrate_a.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterSelection(MDWF_Calibrate_a.CAL_PAR, "Calibration parameter", PARSPECS.PARAMETERS, False))
        self.addParameter(ParameterString(MDWF_Calibrate_a.PAR_NAME, "PEST name for calibration parameter", 'parameter_x'))
        self.addParameter(ParameterNumber(MDWF_Calibrate_a.SUB_ID, "Subbasin ID for calibration parameter", 1,500,1))
        self.addParameter(ParameterNumber(MDWF_Calibrate_a.HRU_ID, "HRU ID for calibration parameter", 1,500,1))
        self.addParameter(ParameterNumber(MDWF_Calibrate_a.PARVAL1, "Starting value of parameter"))
        self.addParameter(ParameterNumber(MDWF_Calibrate_a.PARLBND, "Lower bound of parameter"))
        self.addParameter(ParameterNumber(MDWF_Calibrate_a.PARUBND, "Upper bound of parameter"))


    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(MDWF_Calibrate_a.SRC_FOLDER)
        CAL_PAR = self.getParameterValue(MDWF_Calibrate_a.CAL_PAR)
        CAL_PAR = PARSPECS.PARAMETERS[CAL_PAR]
        PAR_NAME = self.getParameterValue(MDWF_Calibrate_a.PAR_NAME)
        SUB_ID = self.getParameterValue(MDWF_Calibrate_a.SUB_ID)
        HRU_ID = self.getParameterValue(MDWF_Calibrate_a.HRU_ID)
        PARVAL1 = self.getParameterValue(MDWF_Calibrate_a.PARVAL1)
        PARLBND = self.getParameterValue(MDWF_Calibrate_a.PARLBND)
        PARUBND = self.getParameterValue(MDWF_Calibrate_a.PARUBND)

        TEMPLATE_filename, SWAT_filename = SWAT_PEST_utilities.create_PEST_template(SRC_FOLDER, CAL_PAR, PAR_NAME, SUB_ID, HRU_ID, PARVAL1, PARLBND, PARUBND)

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
