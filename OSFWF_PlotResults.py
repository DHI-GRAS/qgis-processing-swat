import os
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterString import ParameterString
from processing.parameters.ParameterSelection import ParameterSelection
from processing.parameters.ParameterNumber import ParameterNumber
from datetime import date, timedelta, datetime
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.pylab import *
import ASS_module4_Results
import ASS_module4_Results_weekly

class OSFWF_PlotResults(GeoAlgorithm):

    ASS_MODE = "ASS_MODE"
    ASS_FOLDER = "ASS_FOLDER"
    STARTDATE = "STARTDATE"
    OBSFILE = "OBSFILE"
    REACH_ID = "REACH_ID"

    def defineCharacteristics(self):
        self.name = "5 - Plot results (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_PlotResults.ASS_FOLDER, "Select assimilation folder", True))
        self.addParameter(ParameterString(OSFWF_PlotResults.STARTDATE, "Issue date (yyyy-mm-dd)", str(date.today())))
        self.addParameter(ParameterFile(OSFWF_PlotResults.OBSFILE, "Select file with corresponding observations",False))
        self.addParameter(ParameterNumber(OSFWF_PlotResults.REACH_ID, "Reach ID", 1, 500, 1))

    def processAlgorithm(self, progress):
        ASS_MODE = self.getParameterValue(OSFWF_PlotResults.ASS_MODE)
        ASS_FOLDER = self.getParameterValue(OSFWF_PlotResults.ASS_FOLDER)
        STARTDATE = self.getParameterValue(OSFWF_PlotResults.STARTDATE)
        OBSFILE = self.getParameterValue(OSFWF_PlotResults.OBSFILE)
        REACH_ID = self.getParameterValue(OSFWF_PlotResults.REACH_ID)

        # Assimilation startdate is 30 days prior to STARTDATE
        ASS_startdate = date2num(num2date(datestr2num(STARTDATE))-timedelta(days = 30))
        # Assimilation enddate is 8 days after STARTDATE
        ASS_enddate = datestr2num(STARTDATE)+ 8

        ASS_module4_Results.Results(OBSFILE, STARTDATE, ASS_startdate, ASS_enddate, ASS_FOLDER, REACH_ID)

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
