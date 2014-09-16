"""
***************************************************************************
   MDWF_Sensan_d.py
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
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterSelection import ParameterSelection
import matplotlib
matplotlib.use('Qt4Agg')
from SWAT_SENSAN_specs import SWAT_SENSAN_specs
SENSAN_specs = SWAT_SENSAN_specs()
import SENSAN_utilities

class MDWF_Sensan_d(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    SNS_FILE = "SNS_FILE"
##    RES_TYPE = "RES_TYPE"

    def defineCharacteristics(self):
        self.name = "5.6 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - SENSAN results"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Sensan_d.SRC_FOLDER, "Select result folder", True))
        self.addParameter(ParameterFile(MDWF_Sensan_d.SNS_FILE, "Select SENSAN control file", False, False))
##        self.addParameter(ParameterSelection(MDWF_Sensan_d.RES_TYPE, "Type of result", SENSAN_specs.RESULT_TYPES, False))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(MDWF_Sensan_d.SRC_FOLDER)
        SNS_FILE = self.getParameterValue(MDWF_Sensan_d.SNS_FILE)
##        RES_TYPE = self.getParameterValue(MDWF_Sensan_d.RES_TYPE)

        if os.path.isfile(SRC_FOLDER+os.sep+SENSAN_specs.RELFLE):
            SNS_INFO = SENSAN_utilities.read_SENSAN_control(SNS_FILE)
            SENSAN_utilities.CSS_SENSAN(SRC_FOLDER, SNS_INFO)
        else:
            raise GeoAlgorithmExecutionException('SENSAN output file ' + SENSAN_specs.RELFLE + ' not found in source directory')

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