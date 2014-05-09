import os
import csv
import numpy
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterBoolean  import ParameterBoolean
from ASS_utilities import ReadNoSubs

class OSFWF_Assimilate_c(GeoAlgorithm):

    BOOLEAN = "BOOLEAN"
    MOD_DESC = "MOD_DESC"
    ASS_FOLDER = "ASS_FOLDER"
    ERR_MOD_FILE = "ERR_MOD_FILE"
    NBRCH = "NBRCH"

    def defineCharacteristics(self):
        self.name = "4.3 - Assimilate observations (OSFWF) - update assimilation file"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterBoolean(OSFWF_Assimilate_c.BOOLEAN, "Replace with global parameters"))
        self.addParameter(ParameterFile(OSFWF_Assimilate_c.MOD_DESC, "Select model description file", False, False))
        self.addParameter(ParameterFile(OSFWF_Assimilate_c.ASS_FOLDER, "Select assimilation folder", True))
        self.addParameter(ParameterFile(OSFWF_Assimilate_c.ERR_MOD_FILE, "Select file with error model parameters", False, False))

    def processAlgorithm(self, progress):

        BOOLEAN = self.getParameterValue(OSFWF_Assimilate_c.BOOLEAN)
        MOD_DESC = self.getParameterValue(OSFWF_Assimilate_c.MOD_DESC)
        ASS_FOLDER = self.getParameterValue(OSFWF_Assimilate_c.ASS_FOLDER)
        ERR_MOD_FILE = self.getParameterValue(OSFWF_Assimilate_c.ERR_MOD_FILE)

        # Extract total number of subbasins from model description file
        NBRCH = ReadNoSubs(MOD_DESC)

        if BOOLEAN == 1:
            filename = ASS_FOLDER + os.sep + 'Assimilationfile.txt'
            if os.path.isfile(filename) & os.path.isfile(ERR_MOD_FILE):
                ass_lines = open(filename,'r').readlines()
                err_lines = open(ERR_MOD_FILE,'r').readlines()
                with open(ASS_FOLDER + os.sep + 'Assimilationfile.txt', 'wb') as csvfile:
                    file_writer = csv.writer(csvfile, delimiter=' ')
                    file_writer.writerow(['Reach'] + ['X'] +  ['K']  + ['DrainsTo'] + ['Runoff'] +['alphaerr'] + ['Loss_fraction'])
                    for j in range(0,NBRCH):
                        l = ass_lines[j+1].split()
                        file_writer.writerow([l[i] for i in range(0,5)]+[err_lines[1].split()[0]] + [l[6]])

                with open(ASS_FOLDER + os.sep + 'Assimilationfile_q.txt', 'wb') as csvfile:
                    file_writer = csv.writer(csvfile, delimiter=' ')
                    file_writer.writerow(['q'])
                    q = numpy.identity(NBRCH)*float(err_lines[1].split()[1])
                    for k in range(0,NBRCH):
                        file_writer.writerow(q[k])
            else:
                raise GeoAlgorithmExecutionException('Assimilationfile.txt, Assimilationfile_q.txt or '+ ERR_MOD_FILE +' not found in assimilation folder '+ ASS_FOLDER +'.')

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
