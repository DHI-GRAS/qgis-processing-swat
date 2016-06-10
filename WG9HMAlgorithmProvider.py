"""
***************************************************************************
   WG9HMAlgorithmProvider.py
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
from PyQt4.QtGui import *
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing_SWAT.WG9HMUtils import WG9HMUtils
from processing.script.WrongScriptException import WrongScriptException
from processing.core.ProcessingConfig import ProcessingConfig, Setting

# Add preloaded algs here
from processing_SWAT.OSFWF_GetGfsData import OSFWF_GetGfsData
from processing_SWAT.OSFWF_GetRfeData import OSFWF_GetRfeData
from processing_SWAT.OSFWF_GetECMWFData import OSFWF_GetECMWFData
from processing_SWAT.OSFWF_GetTRMMData import OSFWF_GetTRMMData
from processing_SWAT.OSFWF_UpdateModelClimateData import OSFWF_UpdateModelClimateData
from processing_SWAT.OSFWF_RunSWAT import OSFWF_RunSWAT
from processing_SWAT.OSFWF_Assimilate_a import OSFWF_Assimilate_a
from processing_SWAT.OSFWF_Assimilate_b import OSFWF_Assimilate_b
from processing_SWAT.OSFWF_Assimilate_c import OSFWF_Assimilate_c
from processing_SWAT.OSFWF_Assimilate_d import OSFWF_Assimilate_d
from processing_SWAT.OSFWF_PlotResults import OSFWF_PlotResults
from processing_SWAT.MDWF_DevSWAT import MDWF_DevSWAT
#from processing_SWAT.MDWF_runBudyko import MDWF_runBudyko
from processing_SWAT.MDWF_GenModelFiles import MDWF_GenModelFiles
from processing_SWAT.MDWF_GenModelClimateData import MDWF_GenModelClimateData
from processing_SWAT.MDWF_RunSWAT import MDWF_RunSWAT
from processing_SWAT.MDWF_PlotResults import MDWF_PlotResults
from processing_SWAT.MDWF_Calibrate_a import MDWF_Calibrate_a
from processing_SWAT.MDWF_Calibrate_b import MDWF_Calibrate_b
from processing_SWAT.MDWF_Calibrate_c import MDWF_Calibrate_c
from processing_SWAT.MDWF_Calibrate_d import MDWF_Calibrate_d
from processing_SWAT.MDWF_Sensan_a import MDWF_Sensan_a
from processing_SWAT.MDWF_Sensan_b import MDWF_Sensan_b
from processing_SWAT.MDWF_Sensan_c import MDWF_Sensan_c
from processing_SWAT.MDWF_Sensan_d import MDWF_Sensan_d
from processing_SWAT.OSFWF_DailyAssimilation import OSFWF_DailyAssimilation

class WG9HMAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(),
                    WG9HMUtils.MAPWINDOW_FOLDER, 'MapWindow folder',
                    WG9HMUtils.mapwindowPath()))

    def unload(self):
        AlgorithmProvider.unload(self)

    def createAlgsList(self):

        # Add preloaded algs here
        self.preloadedAlgs = [OSFWF_GetGfsData(),OSFWF_GetRfeData(),OSFWF_GetECMWFData(),OSFWF_GetTRMMData(),OSFWF_UpdateModelClimateData(),OSFWF_RunSWAT(),
            OSFWF_PlotResults(),MDWF_DevSWAT(),MDWF_GenModelFiles(),MDWF_GenModelClimateData(),MDWF_RunSWAT(),MDWF_PlotResults(),MDWF_Calibrate_a(), MDWF_Calibrate_b(),
            MDWF_Calibrate_c(),MDWF_Calibrate_d(),MDWF_Sensan_a(),MDWF_Sensan_b(),MDWF_Sensan_c(),MDWF_Sensan_d(),OSFWF_Assimilate_a(),OSFWF_Assimilate_b(),OSFWF_Assimilate_c(),OSFWF_Assimilate_d(),
            OSFWF_DailyAssimilation()]


    def getDescription(self):
        return "Product Group 9 Hydrological Model"

    def getName(self):
        return "WG9HM"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs