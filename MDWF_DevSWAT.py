import os
from datetime import date, timedelta, datetime
import numpy
import subprocess
from processing_SWAT.WG9HMUtils import WG9HMUtils
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
##from processing.parameters.ParameterNumber import ParameterNumber
##from processing.parameters.ParameterString import ParameterString

##from ModelFile import ModelFile
##from ClimateStationsSWAT import ClimateStationsSWAT

class MDWF_DevSWAT(GeoAlgorithm):

    def defineCharacteristics(self):
        self.name = "1 - Develop SWAT model (MDWF)"
        self.group = "Model development workflow (MDWF)"

    def processAlgorithm(self, progress):
        progress.setConsoleInfo("Open MapWindow...")


        #MapWindow_path = 'C:\Program Files (x86)\MapWindow\MapWindow.exe'
        MapWindow_path = os.path.join(WG9HMUtils.mapwindowPath(),'MapWindow.exe')
        subprocess.call([MapWindow_path])


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
