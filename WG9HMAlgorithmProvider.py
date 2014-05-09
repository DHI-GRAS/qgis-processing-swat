import os
from PyQt4.QtGui import *
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing_SWAT.WG9HMAlgorithm import WG9HMAlgorithm
from processing.script.WrongScriptException import WrongScriptException

# Add preloaded algs here
from processing_SWAT.OSFWF_GetGfsData import OSFWF_GetGfsData
from processing_SWAT.OSFWF_GetRfeData import OSFWF_GetRfeData
from processing_SWAT.OSFWF_GetECMWFData import OSFWF_GetECMWFData
from processing_SWAT.OSFWF_UpdateModelClimateData import OSFWF_UpdateModelClimateData
from processing_SWAT.OSFWF_RunSWAT import OSFWF_RunSWAT
from processing_SWAT.OSFWF_Assimilate_a import OSFWF_Assimilate_a
from processing_SWAT.OSFWF_Assimilate_b import OSFWF_Assimilate_b
from processing_SWAT.OSFWF_Assimilate_c import OSFWF_Assimilate_c
from processing_SWAT.OSFWF_Assimilate_d import OSFWF_Assimilate_d
from processing_SWAT.OSFWF_PlotResults import OSFWF_PlotResults
from processing_SWAT.MDWF_DevSWAT import MDWF_DevSWAT
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

class WG9HMAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = False
        self.createAlgsList() #preloading algorithms to speed up

    def scriptsFolder(self):
        '''The folder where script algorithms are stored'''
        return os.path.dirname(__file__) + "/scripts"

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)

    def createAlgsList(self):

        # Add preloaded algs here
        self.preloadedAlgs = [OSFWF_GetGfsData(),OSFWF_GetRfeData(),OSFWF_GetECMWFData(),OSFWF_UpdateModelClimateData(),OSFWF_RunSWAT(),
            OSFWF_PlotResults(),MDWF_DevSWAT(),MDWF_GenModelFiles(),MDWF_GenModelClimateData(),MDWF_RunSWAT(),MDWF_PlotResults(),MDWF_Calibrate_a(), MDWF_Calibrate_b(),
            MDWF_Calibrate_c(),MDWF_Calibrate_d(),MDWF_Sensan_a(),MDWF_Sensan_b(),MDWF_Sensan_c(),MDWF_Sensan_d(),OSFWF_Assimilate_a(),OSFWF_Assimilate_b(),OSFWF_Assimilate_c(),OSFWF_Assimilate_d()]

        folder = self.scriptsFolder()
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith("py"):
                try:
                    fullpath = os.path.join(self.scriptsFolder(), descriptionFile)
                    alg = WG9HMAlgorithm(fullpath)
                    self.preloadedAlgs.append(alg)
                except WrongScriptException,e:
                    ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,e.msg)

    def getDescription(self):
        return "Product Group 9 Hydrological Model"

    def getName(self):
        return "WG9HM"

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

    def _loadAlgorithms(self):
        self.algs = self.preloadedAlgs