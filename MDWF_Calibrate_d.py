import os
from datetime import date, timedelta, datetime
import numpy
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterSelection import ParameterSelection
from ModelFile import ModelFile
from SWAT_PEST_specs import SWAT_PEST_specs

class MDWF_Calibrate_d(GeoAlgorithm):

    PEST_mode = "PEST_mode"
    SRC_FOLDER = "SRC_FOLDER"
    CONTROL_FILE = "CONTROL_FILE"


    def defineCharacteristics(self):
        self.name = "5.8 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - run PEST"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterSelection(MDWF_Calibrate_d.PEST_mode, "Calibration algorithm", ['PEST','SCEUA_P','CMAES_P'], False))
        self.addParameter(ParameterFile(MDWF_Calibrate_d.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(MDWF_Calibrate_d.CONTROL_FILE, "Select PEST control file", False, False))


    def processAlgorithm(self, progress):
        PEST_mode = self.getParameterValue(MDWF_Calibrate_d.PEST_mode)
        SRC_FOLDER = self.getParameterValue(MDWF_Calibrate_d.SRC_FOLDER)
        CONTROL_FILE = self.getParameterValue(MDWF_Calibrate_d.CONTROL_FILE)
        CONTROL_FILE = os.path.split(CONTROL_FILE)[1]
        pestspecs = SWAT_PEST_specs()

        # Writing PEST batch file
        batname = SRC_FOLDER + os.sep + 'WOIS_PEST_run.bat'
        batfile = open(batname,'w')
        batfile.writelines('@ECHO OFF\r\n')
        batfile.writelines('cd ' + SRC_FOLDER + '\r\n')
        if PEST_mode == 0:
            batfile.writelines('"'+pestspecs.PESTexeFolder + os.sep + 'pest.exe" ' + CONTROL_FILE + '\r\n')
        elif PEST_mode ==1:
            batfile.writelines('"'+pestspecs.PESTexeFolder + os.sep + 'sceua_p.exe" ' + CONTROL_FILE + '\r\n')
        else:
            batfile.writelines('"'+pestspecs.PESTexeFolder + os.sep + 'cmaes_p.exe" ' + CONTROL_FILE + '\r\n')
        batfile.writelines('@PAUSE\r\n')
        batfile.close()

        # Running PEST
        currpath = os.getcwd()
        os.chdir(SRC_FOLDER)
        runres = subprocess.call(batname)
        os.chdir(currpath)



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
