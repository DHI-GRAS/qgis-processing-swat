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
from ASS_utilities import ReadNoSubs

class MDWF_Calibrate_b(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    MOD_DESC = "MOD_DESC"
    OBS_FILE = "OBS_FILE"
    OBS_GROUP = "OBS_GROUP"
##    SUB_ID = "SUB_ID"
    TEMP_RES = "TEMP_RES"

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
