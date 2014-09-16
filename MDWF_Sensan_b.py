"""
***************************************************************************
   MDWF_Sensan_b.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

import os
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from SWAT_SENSAN_specs import SWAT_SENSAN_specs
from ModelFile import ModelFile
from ParVarFile import ParVarFile

class MDWF_Sensan_b(GeoAlgorithm):

    MODEL_FILE = "MODEL_FILE"
    SRC_FOLDER = "SRC_FOLDER"
    PARVAR = "PARVAR"
    SWAT_EXE = "SWAT_EXE"

    def defineCharacteristics(self):
        self.name = "5.4 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - generate SENSAN control file"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Sensan_b.MODEL_FILE, "Model description file", False, False))
        self.addParameter(ParameterFile(MDWF_Sensan_b.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterFile(MDWF_Sensan_b.PARVAR, "Parameter variation file", False, False))
        self.addParameter(ParameterFile(MDWF_Sensan_b.SWAT_EXE, "SWAT executable", False, False))

    def processAlgorithm(self, progress):
        sensanspecs = SWAT_SENSAN_specs()
        MODEL_FILE = self.getParameterValue(MDWF_Sensan_b.MODEL_FILE)
        SRC_FOLDER = self.getParameterValue(MDWF_Sensan_b.SRC_FOLDER)
        PARVAR_FILE = self.getParameterValue(MDWF_Sensan_b.PARVAR)
        SWAT_EXE = self.getParameterValue(MDWF_Sensan_b.SWAT_EXE)
        model = ModelFile(MODEL_FILE)
        ctlfilename = SRC_FOLDER + os.sep + model.desc['ModelName'] + '.sns'
        ctlfile = open(ctlfilename,'w')
        ctlfile.writelines(sensanspecs.CFfirstline + '\n')
        ctlfile.writelines('* control data\n')
        ctlfile.writelines(str(sensanspecs.SCREENDISP).ljust(10)+'\n')
        #find number of parameters
        filelist = os.listdir(SRC_FOLDER)
        NPAR = 0
        PARBLOCK = []
        for f in filelist:
            if '.pbf' in f:
                NPAR = NPAR + 1
        #verify parameter variation file
        ParVarFile(PARVAR_FILE, NPAR)
        #find number of observations
        OBSBLOCK = []
        for f in filelist:
            if 'observation_block.obf' in f:
                cobsblock = open(SRC_FOLDER + os.sep + f).readlines()
                for i in range(0,len(cobsblock)):
                    OBSBLOCK.append(cobsblock[i])
        NOBS = len(OBSBLOCK)
        if NPAR > 0 and NOBS > 0:
            ctlfile.writelines(str(NPAR).ljust(4) + str(NOBS).ljust(7) + '\n')
        else:
            raise GeoAlgorithmExecutionException('Number of observations and number of parameters must be larger than zero')
        #find number of template files and prepare template block
        NTPLFLE = 0
        TPLBLOCK = []
        for f in filelist:
            if '.tpl' in f:
                TPLBLOCK.append(f + ' ' + f.split('.')[0].split('_')[0] + '.' + f.split('.')[0].split('_')[1] + '\n')
                NTPLFLE = NTPLFLE + 1
        #find number of instruction files and prepare instruction block
        NINSFLE = 0
        INSBLOCK = []
        for f in filelist:
            if '.ins' in f:
                INSBLOCK.append(f + ' output.rch\n')
                NINSFLE = NINSFLE + 1
        if NTPLFLE > 0 and NINSFLE > 0:
            ctlfile.writelines(str(NTPLFLE).ljust(4) + str(NINSFLE).ljust(4) + str(sensanspecs.PRECIS).ljust(7) + str(sensanspecs.DPOINT).ljust(8) + '\n')
        else:
            raise GeoAlgorithmExecutionException('Number of template files and number of instruction files must be larger than zero')
        ctlfile.writelines('* sensan files\n')
        ctlfile.writelines(os.path.split(PARVAR_FILE)[1] + '\n')
        ctlfile.writelines(str(sensanspecs.ABSFLE) + '\n')
        ctlfile.writelines(str(sensanspecs.RELFLE) + '\n')
        ctlfile.writelines(str(sensanspecs.SENSFLE) + '\n')
        ctlfile.writelines('* model command line\n')
        ctlfile.writelines(SWAT_EXE + '> nul\n')
        ctlfile.writelines('* model input/output\n')
        ctlfile.writelines(TPLBLOCK)
        ctlfile.writelines(INSBLOCK)
        ctlfile.close()

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
