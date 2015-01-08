"""
***************************************************************************
   MDWF_Calibate_c.py
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
from datetime import date, timedelta, datetime
import numpy
import subprocess
from PyQt4 import QtGui
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
from SWAT_PEST_specs import SWAT_PEST_specs
from SWAT_parameter_specs import SWAT_parameter_specs
from ModelFile import ModelFile

class MDWF_Calibrate_c(SWATAlgorithm):

    MODEL_FILE = "MODEL_FILE"
    SRC_FOLDER = "SRC_FOLDER"
    OBGNME = "OBGNME"
    SWAT_EXE = "SWAT_EXE"

    def __init__(self):
        super(MDWF_Calibrate_c, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "5.7 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - generate PEST control file"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Calibrate_c.MODEL_FILE, "Model description file", False, False))
        self.addParameter(ParameterFile(MDWF_Calibrate_c.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterString(MDWF_Calibrate_c.OBGNME, "PEST name of observation group", 'discharge'))
        self.addParameter(ParameterFile(MDWF_Calibrate_c.SWAT_EXE, "SWAT executable", False, False))

    def processAlgorithm(self, progress):
        pestspecs = SWAT_PEST_specs()
        parspecs = SWAT_parameter_specs()
        MODEL_FILE = self.getParameterValue(MDWF_Calibrate_c.MODEL_FILE)
        SRC_FOLDER = self.getParameterValue(MDWF_Calibrate_c.SRC_FOLDER)
        OBGNME = self.getParameterValue(MDWF_Calibrate_c.OBGNME)
        SWAT_EXE = self.getParameterValue(MDWF_Calibrate_c.SWAT_EXE)
        model = ModelFile(MODEL_FILE)
        ctlfilename = SRC_FOLDER + os.sep + model.desc['ModelName'] + '.pst'
        ctlfile = open(ctlfilename,'w')
        ctlfile.writelines(pestspecs.CFfirstline + '\r\n')
        ctlfile.writelines('* control data\r\n')
        ctlfile.writelines(pestspecs.RSTFLE + ' ' + pestspecs.PESTMODE + '\r\n')
        #find number of parameters and prepare the parameter block
        filelist = os.listdir(SRC_FOLDER)
        NPAR = 0
        PARBLOCK = []
        for f in filelist:
            if '.pbf' in f:
                NPAR = NPAR + 1
                PARBLOCK.append(open(SRC_FOLDER + os.sep + f).readlines()[0] + '\r\n')
        #find number of observations and prepare the observation block
        OBSBLOCK = []
        for f in filelist:
            if '.obf' in f:
                cobsblock = open(SRC_FOLDER + os.sep + f).readlines()
                for i in range(0,len(cobsblock)):
                    OBSBLOCK.append(cobsblock[i])
        NOBS = len(OBSBLOCK)
        if NPAR > 0 and NOBS > 0:
            ctlfile.writelines(str(NPAR).ljust(4) + str(NOBS).ljust(7) + str(pestspecs.NPARGP).ljust(4) + str(pestspecs.NPRIOR).ljust(4) + str(pestspecs.NOBSGP).ljust(4) + '\r\n')
        else:
            raise GeoAlgorithmExecutionException('Number of observations and number of parameters must be larger than zero')
        #find number of template files and prepare template block
        NTPLFLE = 0
        TPLBLOCK = []
        for f in filelist:
            if '.tpl' in f:
                TPLBLOCK.append(f + ' ' + f.split('.')[0].split('_')[0] + '.' + f.split('.')[0].split('_')[1] + '\r\n')
                NTPLFLE = NTPLFLE + 1
        #find number of instruction files and prepare instruction block
        NINSFLE = 0
        INSBLOCK = []
        for f in filelist:
            if '.ins' in f:
                INSBLOCK.append(f + ' output.rch\r\n')
                NINSFLE = NINSFLE + 1
        if NTPLFLE > 0 and NINSFLE > 0:
            ctlfile.writelines(str(NTPLFLE).ljust(4) + str(NINSFLE).ljust(4) + str(pestspecs.PRECIS).ljust(7) + str(pestspecs.DPOINT).ljust(8) + str(pestspecs.NUMCOM).ljust(3) + str(pestspecs.JACFILE).ljust(3) + str(pestspecs.MESSFILE).ljust(3) + '\r\n')
        else:
            raise GeoAlgorithmExecutionException('Number of template files and number of instruction files must be larger than zero')
        ctlfile.writelines(str(pestspecs.RLAMBDA1).ljust(6) + str(pestspecs.RLAMFAC).ljust(6) + str(pestspecs.PHIRATSUF).ljust(6) + str(pestspecs.PHIREDLAM).ljust(6) + str(pestspecs.NUMLAM) + '\r\n')
        ctlfile.writelines(str(pestspecs.RELPARMAX).ljust(6) + str(pestspecs.FACPARMAX).ljust(6) + str(pestspecs.FACORIG) + '\r\n')
        ctlfile.writelines(str(pestspecs.PHIREDSWH) + '\r\n')
        ctlfile.writelines(str(pestspecs.NOPTMAX).ljust(5) + str(pestspecs.PHIREDSTP).ljust(7) + str(pestspecs.NPHISTP).ljust(4) + str(pestspecs.NPHINORED).ljust(4) + str(pestspecs.RELPARSTP).ljust(7) + str(pestspecs.NRELPAR) + '\r\n')
        ctlfile.writelines(str(pestspecs.ICOV).ljust(3) + str(pestspecs.ICOR).ljust(3) + str(pestspecs.IEIG) + '\r\n')
        ctlfile.writelines('* parameter groups\r\n')
        for i in range(0,pestspecs.NPARGP):
            ctlfile.writelines(parspecs.PARAMETERS[i].ljust(13) + parspecs.INCTYP[i].ljust(9) + str(parspecs.DERINC[i]).ljust(7) + str(parspecs.DERINCLB[i]).ljust(7) + parspecs.FORCEN[i].ljust(9) + str(parspecs.DERINCMUL[i]).ljust(7) +parspecs.DERMTHD[i] + '\r\n')
        ctlfile.writelines('* parameter data\r\n')
        ctlfile.writelines(PARBLOCK)
        ctlfile.writelines('* observation groups\r\n')
        ctlfile.writelines(OBGNME + '\r\n')
        ctlfile.writelines('* observation data\r\n')
        ctlfile.writelines(OBSBLOCK)
        ctlfile.writelines('* model command line\r\n')
        ctlfile.writelines('pest_swatrun.bat\r\n')
        batfile = open(SRC_FOLDER + os.sep + 'pest_swatrun.bat','w')
        batfile.writelines('@ECHO OFF \r\n')
        batfile.writelines('cd ' + SRC_FOLDER + '\r\n')
        batfile.writelines(SWAT_EXE + '> nul\r\n')
        batfile.close()
        ctlfile.writelines('* model input/output\r\n')
        ctlfile.writelines(TPLBLOCK)
        ctlfile.writelines(INSBLOCK)
        ctlfile.close()

