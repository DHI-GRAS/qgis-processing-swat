"""
***************************************************************************
   AMDWF_DevSWAT.py
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
from processing_SWAT.WG9HMUtils import WG9HMUtils
from PyQt4 import QtGui
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm

##from ModelFile import ModelFile
##from ClimateStationsSWAT import ClimateStationsSWAT

class MDWF_DevSWAT(SWATAlgorithm):
    
    def __init__(self):
        super(MDWF_DevSWAT, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "1 - Develop SWAT model (MDWF)"
        self.group = "Model development workflow (MDWF)"

    def processAlgorithm(self, progress):
        progress.setConsoleInfo("Open MapWindow...")

        MapWindow_path = os.path.join(WG9HMUtils.mapwindowPath(),'MapWindow.exe')
        subprocess.Popen([MapWindow_path])

