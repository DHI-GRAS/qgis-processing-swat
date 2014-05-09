import os
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.parameters.ParameterFile import ParameterFile
from SWAT_PEST_specs import SWAT_PEST_specs

class MDWF_Sensan_c(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    CONTROL_FILE = "CONTROL_FILE"


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
