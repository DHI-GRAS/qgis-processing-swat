import os
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterString import ParameterString
from processing.parameters.ParameterSelection import ParameterSelection
from datetime import date, timedelta, datetime
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import read_SWAT_out
from SWAT_output_format_specs import SWAT_output_format_specs

RES_OUTSPECS = SWAT_output_format_specs()

class MDWF_PlotResults(GeoAlgorithm):

    RES_FOLDER = "RES_FOLDER"
    RES_TYPE = "RES_TYPE"
    RES_VAR = "RES_VAR"
    REACH_ID = "REACH_ID"
    SUB_ID = "SUB_ID"
    HRU_ID = "HRU_ID"
    RES_OBSFILE = "RES_OBSFILE"
    TEMP_RES = "TEMP_RES"

    def defineCharacteristics(self):
        self.name = "6 - Plot Results (MDWF)"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_PlotResults.RES_FOLDER, "Select results folder", True))
        self.addParameter(ParameterSelection(MDWF_PlotResults.TEMP_RES, "Temporal resolution", ['Daily','Weekly','Monthly'], False))
        self.addParameter(ParameterSelection(MDWF_PlotResults.RES_TYPE, "Type of result", RES_OUTSPECS.RESULT_TYPES, False))
        param = ParameterSelection(MDWF_PlotResults.RES_VAR, "Variable", RES_OUTSPECS.RESULT_VARIABLES , False)
        param.isAdvanced = False
        self.addParameter(param)
        param = ParameterNumber(MDWF_PlotResults.REACH_ID, "Reach ID", 1, 500, 1)
        param.isAdvanced = False
        self.addParameter(param)
        param = ParameterNumber(MDWF_PlotResults.SUB_ID, "Sub-basin ID", 1, 500, 1)
        param.isAdvanced = False
        self.addParameter(param)
        param = ParameterNumber(MDWF_PlotResults.HRU_ID, "HRU ID", 1, 500, 1)
        param.isAdvanced = False
        self.addParameter(param)
        self.addParameter(ParameterFile(MDWF_PlotResults.RES_OBSFILE, "Select file with corresponding observations", False))

    def processAlgorithm(self, progress):
        RES_FOLDER = self.getParameterValue(MDWF_PlotResults.RES_FOLDER)
        RES_TYPE = self.getParameterValue(MDWF_PlotResults.RES_TYPE)
        RES_VAR = self.getParameterValue(MDWF_PlotResults.RES_VAR)
        REACH_ID = self.getParameterValue(MDWF_PlotResults.REACH_ID)
        SUB_ID = self.getParameterValue(MDWF_PlotResults.SUB_ID)
        HRU_ID = self.getParameterValue(MDWF_PlotResults.HRU_ID)
        RES_OBSFILE = self.getParameterValue(MDWF_PlotResults.RES_OBSFILE)
        TEMP_RES = self.getParameterValue(MDWF_PlotResults.TEMP_RES)

        if RES_TYPE == 0:
            RES_UNIT = RES_OUTSPECS.REACH_UNITS[RES_VAR]
            RES_VARCOL = RES_OUTSPECS.REACH_RES_COLS[RES_VAR]
            RES_VAR = RES_OUTSPECS.RESULT_VARIABLES[RES_VAR]
##            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.REACH_DELIMITER,RES_OUTSPECS.REACH_SKIPROWS,RES_OUTSPECS.REACH_OUTNAME)
            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.REACH_SKIPROWS,RES_OUTSPECS.REACH_OUTNAME)
            data_ex = read_SWAT_out.reach_SWAT_ts(data,REACH_ID,RES_VARCOL,RES_VAR)
            stime = read_SWAT_out.read_SWAT_time(RES_FOLDER)
            if (TEMP_RES == 2) & (stime[-1] != 0):
				raise GeoAlgorithmExecutionException('According to master watershed file (file.cio) the reach output file is not printed with a monthly time step.')
            else:
				read_SWAT_out.reach_tsplot(stime,data_ex,REACH_ID,RES_VAR,RES_UNIT,RES_FOLDER,RES_OUTSPECS.PYEX_DATE_OFFSET,RES_OBSFILE,TEMP_RES)
        elif RES_TYPE == 1:
            RES_UNIT = RES_OUTSPECS.SUB_UNITS[RES_VAR]
            RES_VARCOL = RES_OUTSPECS.SUB_RES_COLS[RES_VAR]
            RES_VAR = RES_OUTSPECS.RESULT_VARIABLES[RES_VAR]
##            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.SUB_DELIMITER,RES_OUTSPECS.SUB_SKIPROWS,RES_OUTSPECS.SUB_OUTNAME)
            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.SUB_SKIPROWS,RES_OUTSPECS.SUB_OUTNAME)
            data_ex = read_SWAT_out.sub_SWAT_ts(data,SUB_ID,RES_VARCOL,RES_VAR)
            stime = read_SWAT_out.read_SWAT_time(RES_FOLDER)
            read_SWAT_out.sub_tsplot(stime,data_ex,SUB_ID,RES_VAR,RES_UNIT,RES_FOLDER,RES_OUTSPECS.PYEX_DATE_OFFSET,RES_OBSFILE)
        elif RES_TYPE == 2:
            RES_UNIT = RES_OUTSPECS.HRU_UNITS[RES_VAR]
            RES_VARCOL = RES_OUTSPECS.HRU_RES_COLS[RES_VAR]
            RES_VAR = RES_OUTSPECS.RESULT_VARIABLES[RES_VAR]
##            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.HRU_DELIMITER,RES_OUTSPECS.HRU_SKIPROWS,RES_OUTSPECS.HRU_OUTNAME)
            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.HRU_SKIPROWS,RES_OUTSPECS.HRU_OUTNAME)
            data_ex = read_SWAT_out.hru_SWAT_ts(data,SUB_ID,HRU_ID,RES_VARCOL,RES_VAR)
            stime = read_SWAT_out.read_SWAT_time(RES_FOLDER)
            read_SWAT_out.hru_tsplot(stime,data_ex,SUB_ID,HRU_ID,RES_VAR,RES_UNIT,RES_FOLDER,RES_OUTSPECS.PYEX_DATE_OFFSET,RES_OBSFILE)
        elif RES_TYPE == 3:
            RES_UNIT = RES_OUTSPECS.RSV_UNITS[RES_VAR]
            RES_VARCOL = RES_OUTSPECS.RSV_RES_COLS[RES_VAR]
            RES_VAR = RES_OUTSPECS.RESULT_VARIABLES[RES_VAR]
            data = read_SWAT_out.read_SWAT_out(RES_FOLDER,RES_OUTSPECS.RSV_SKIPROWS,RES_OUTSPECS.RSV_OUTNAME)
            (data_ex, RSV_ID) = read_SWAT_out.rsv_SWAT_ts(RES_FOLDER,data,SUB_ID,RES_VARCOL,RES_VAR)
            stime = read_SWAT_out.read_SWAT_time(RES_FOLDER)
            read_SWAT_out.rsv_tsplot(stime,data_ex,SUB_ID,RSV_ID,RES_VAR,RES_UNIT,RES_FOLDER,RES_OUTSPECS.PYEX_DATE_OFFSET,RES_OBSFILE)
        else:
            raise GeoAlgorithmExecutionException('Result type not supported at the moment')

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

