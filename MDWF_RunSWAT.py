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
from processing.parameters.ParameterString import ParameterString
from ClimateStationsSWAT import ClimateStationsSWAT
from ModelFile import ModelFile

class MDWF_RunSWAT(GeoAlgorithm):

    MODEL_FILE = "MODEL_FILE"
    IO_FOLDER = "IO_FOLDER"
    SWAT_EXE = "SWAT_EXE"
    UPDATE_YN = "UPDATE_YN"
    MODEL_NEWENDDATE ="MODEL_NEWENDDATE"

    def defineCharacteristics(self):
        self.name = "4 - Run SWAT model (MDWF)"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_RunSWAT.MODEL_FILE, "Model description file", False, False))
        self.addParameter(ParameterFile(MDWF_RunSWAT.IO_FOLDER, "Model input/output folder", True))
        self.addParameter(ParameterFile(MDWF_RunSWAT.SWAT_EXE, "SWAT executable", False, False))
        self.addParameter(ParameterSelection(MDWF_RunSWAT.UPDATE_YN, "Update simulation period?", ['Yes','No'], False))
        self.addParameter(ParameterString(MDWF_RunSWAT.MODEL_NEWENDDATE, "New end date of simulation period YYYYMMDD"))

    def processAlgorithm(self, progress):
        MODEL_FILE = self.getParameterValue(MDWF_RunSWAT.MODEL_FILE)
        model = ModelFile(MODEL_FILE)
        CSTATIONS_FILE = model.Path + os.sep + model.desc['Stations']
        IO_FOLDER = self.getParameterValue(MDWF_RunSWAT.IO_FOLDER)
        SWAT_EXE = self.getParameterValue(MDWF_RunSWAT.SWAT_EXE)
        UPDATE_YN = self.getParameterValue(MDWF_RunSWAT.UPDATE_YN)
        MODEL_NEWENDDATE = self.getParameterValue(MDWF_RunSWAT.MODEL_NEWENDDATE)

        if UPDATE_YN == 0:
            # Updating climate files
            CSTATIONS = ClimateStationsSWAT(CSTATIONS_FILE)
            log_file = open(IO_FOLDER + os.sep + "cstations_log.txt", "w")
            last_pcp_date,last_tmp_date = CSTATIONS.writeSWATrunClimateFiles(IO_FOLDER,log_file)
            log_file.close()

            # Updating cio file
            last_date = date(int(MODEL_NEWENDDATE[0:4]),int(MODEL_NEWENDDATE[4:6]),int(MODEL_NEWENDDATE[6:8]))
            if last_date > last_pcp_date or last_date > last_tmp_date:
                raise GeoAlgorithmExecutionException('Climate data not available up to ' + MODEL_NEWENDDATE)

            if os.path.isfile(IO_FOLDER + os.sep + "file.cio"):
                cio_file = open(IO_FOLDER + os.sep + "file.cio", "r")
                cio=cio_file.readlines()
                cio_file.close()
                startyear = int(cio[8][0:16])
                nbyears = last_date.year - startyear + 1
                endjulianday = (last_date-date(last_date.year,1,1)).days + 1
                nbyearline = str(nbyears).rjust(16) + cio[7][16:len(cio[7])]
                endjdayline = str(endjulianday).rjust(16) + cio[10][16:len(cio[10])]
                cio[7]=nbyearline
                cio[10]=endjdayline
                cio_file = open(IO_FOLDER + os.sep + "file.cio", "w")
                cio_file.writelines(cio)
                cio_file.close()
            else:
                raise GeoAlgorithmExecutionException('cio-file ' + IO_FOLDER + os.sep + "file.cio" + ' does not exist')

        # Running SWAT
        currpath = os.getcwd()
        os.chdir(IO_FOLDER)
        runres = subprocess.call(SWAT_EXE)
        os.chdir(currpath)
        if runres != 0:
            raise GeoAlgorithmExecutionException('SWAT run unsuccessful')


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