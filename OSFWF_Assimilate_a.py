import os
from datetime import date, timedelta
from matplotlib.pylab import *
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterString import ParameterString
from processing.parameters.ParameterNumber import ParameterNumber
from read_SWAT_out import read_SWAT_time
from SWAT_output_format_specs import SWAT_output_format_specs
from ASS_utilities import ReadNoSubs
import ASS_module1_PrepData

OUTSPECS = SWAT_output_format_specs()

class OSFWF_Assimilate_a(GeoAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    MOD_DESC = "MOD_DESC"
    ASS_FOLDER = "ASS_FOLDER"

    def defineCharacteristics(self):
        self.name = "4.1 - Assimilate observations (OSFWF) - prepare input data"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.MOD_DESC, "Select model description file", False, False))
        self.addParameter(ParameterFile(OSFWF_Assimilate_a.ASS_FOLDER, "Select assimilation folder", True))

    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(OSFWF_Assimilate_a.SRC_FOLDER)
        MOD_DESC = self.getParameterValue(OSFWF_Assimilate_a.MOD_DESC)
        ASS_FOLDER = self.getParameterValue(OSFWF_Assimilate_a.ASS_FOLDER)

        # Extract total number of subbasins from model description file
        NBRCH = ReadNoSubs(MOD_DESC)

        # Get startdate from SWAT file.cio and compare with startdate of assimilation to determine header in SWAT output files
        SWAT_time_info = read_SWAT_time(SRC_FOLDER)
        SWAT_startdate = date2num(date(int(SWAT_time_info[1]),1,1) + timedelta(days=int(SWAT_time_info[2])-1))
        if SWAT_time_info[4] > 0: # Account for NYSKIP>0
            SWAT_startdate = date2num(date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1))
        SWAT_enddate = date2num(date(int(SWAT_time_info[0]+SWAT_time_info[1]-1),1,1)) + SWAT_time_info[3]-1
        header = OUTSPECS.REACH_SKIPROWS

        ASS_module1_PrepData.CreateTextFiles(NBRCH, SRC_FOLDER, ASS_FOLDER, header, SWAT_startdate, SWAT_enddate)

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
