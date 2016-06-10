"""
***************************************************************************
   MDWF_Sensan_c.py
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
import subprocess
from PyQt4 import QtGui
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
from SWAT_PEST_specs import SWAT_PEST_specs

class MDWF_Sensan_c(SWATAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    CONTROL_FILE = "CONTROL_FILE"

    def __init__(self):
        super(MDWF_Sensan_c, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "5.5 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - run SENSAN"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Sensan_c.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(MDWF_Sensan_c.CONTROL_FILE, "Select SENSAN control file", False, False))


    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(MDWF_Sensan_c.SRC_FOLDER)
        CONTROL_FILE = self.getParameterValue(MDWF_Sensan_c.CONTROL_FILE)
        CONTROL_FILE = os.path.split(CONTROL_FILE)[1]
        pestspecs = SWAT_PEST_specs()

        # Writing PEST batch file
        batname = SRC_FOLDER + os.sep + 'WOIS_SENSAN_run.bat'
        batfile = open(batname,'w')
        batfile.writelines('@ECHO OFF\r\n')
        batfile.writelines('cd ' + SRC_FOLDER + '\r\n')
        batfile.writelines('"'+pestspecs.PESTexeFolder + os.sep + 'sensan.exe" ' + CONTROL_FILE + '\r\n')
        batfile.writelines('@PAUSE\r\n')
        batfile.close()

        # Running SENSAN
        currpath = os.getcwd()
        os.chdir(SRC_FOLDER)
        runres = subprocess.call(batname)
        os.chdir(currpath)

