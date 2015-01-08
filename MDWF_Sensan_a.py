"""
***************************************************************************
   MDWF_Sensan_a.py
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
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
from SWAT_SENSAN_specs import SWAT_SENSAN_specs

SENSAN_specs = SWAT_SENSAN_specs()

class MDWF_Sensan_a(SWATAlgorithm):

    SRC_FOLDER = "SRC_FOLDER"
    PAR_SRC = "PAR_SRC"
    PST_FILE = "PST_FILE"
    PAR_FILE = "PAR_FILE"
    PCT_DEV = "PCT_DEV"

    def __init__(self):
        super(MDWF_Sensan_a, self).__init__(__file__)

    def defineCharacteristics(self):
        self.name = "5.3 - Sensitivity analysis and calibration of SWAT model with PEST (MDWF) - generate parameter variation file"
        self.group = "Model development workflow (MDWF)"
        self.addParameter(ParameterFile(MDWF_Sensan_a.SRC_FOLDER, "Select model source folder", True))
        self.addParameter(ParameterSelection(MDWF_Sensan_a.PAR_SRC, "Select source for parameter variation", ['Initial parameter values in PEST control file (.pst)','Initial parameter values defined when creating template files (.pbf)','Optimal parameter values output file from PEST (.par)'], False))
        self.addParameter(ParameterFile(MDWF_Sensan_a.PST_FILE, "Select PEST control file", False))
        self.addParameter(ParameterFile(MDWF_Sensan_a.PAR_FILE, "Select PEST output parameter file", False))
        self.addParameter(ParameterNumber(MDWF_Sensan_a.PCT_DEV, "Percent deviation in parameter values"))


    def processAlgorithm(self, progress):
        SRC_FOLDER = self.getParameterValue(MDWF_Sensan_a.SRC_FOLDER)
        PAR_SRC = self.getParameterValue(MDWF_Sensan_a.PAR_SRC)
        PST_FILE = self.getParameterValue(MDWF_Sensan_a.PST_FILE)
        PAR_FILE = self.getParameterValue(MDWF_Sensan_a.PAR_FILE)
        PCT_DEV = self.getParameterValue(MDWF_Sensan_a.PCT_DEV)
        pct_devfile = open(SRC_FOLDER + os.sep + 'pct_dev.dat','w')
        pct_devfile.writelines(str(PCT_DEV)+'\r\n')
        pct_devfile.close()
        pvfilename = SRC_FOLDER + os.sep + SENSAN_specs.VARFLE
        pvfile = open(pvfilename,'w')
        PARNAME = []
        PARVAL1 = []
        PARLBND = []
        PARUBND = []
        # Find number of parameters and prepare the parameter variation block
        if PAR_SRC == 0:
            if os.path.isfile(PST_FILE):
                pst_lines = open(PST_FILE,'r').readlines()
                no_par = int(pst_lines[3].split()[0])
                no_obsgr = int(pst_lines[3].split()[2])
                for i in range(no_obsgr+12,no_obsgr+12+no_par):
                    PARNAME.append(pst_lines[i].split()[0])
                    PARVAL1.append(pst_lines[i].split()[3])
                    PARLBND.append(pst_lines[i].split()[4])
                    PARUBND.append(pst_lines[i].split()[5])
            else:
                raise GeoAlgorithmExecutionException('File ' + PST_FILE + ' does not exist. Please chose another source for parameter variation.')
        elif PAR_SRC == 1:
            filelist = os.listdir(SRC_FOLDER)
            for f in filelist:
                if '.pbf' in f:
                    PARNAME.append(open(SRC_FOLDER + os.sep +f,'r').readlines()[0].split()[0])
                    PARVAL1.append(open(SRC_FOLDER + os.sep +f,'r').readlines()[0].split()[3])
                    PARLBND.append(open(SRC_FOLDER + os.sep +f,'r').readlines()[0].split()[4])
                    PARUBND.append(open(SRC_FOLDER + os.sep +f,'r').readlines()[0].split()[5])
        elif PAR_SRC == 2:
            if os.path.isfile(PAR_FILE):
                par_lines = open(PAR_FILE,'r').readlines()
                no_par = len(par_lines)-1
                for i in range(1,no_par+1):
                    PARNAME.append(par_lines[i].split()[0])
                    PARVAL1.append(par_lines[i].split()[1])
                pst_lines = open(PST_FILE,'r').readlines()
                no_par = int(pst_lines[3].split()[0])
                no_obsgr = int(pst_lines[3].split()[2])
                for i in range(no_obsgr+12,no_obsgr+12+no_par):
                    PARLBND.append(pst_lines[i].split()[4])
                    PARUBND.append(pst_lines[i].split()[5])
            else:
                raise GeoAlgorithmExecutionException('File ' + PAR_FILE + ' does not exist. Please chose another source for parameter variation.')

        # Write header and baseline parameter set
        for i in range(0,len(PARNAME)):
            pvfile.writelines(PARNAME[i] + '\t')
        pvfile.writelines('\r\n')
        for i in range(0,len(PARVAL1)):
            pvfile.writelines(PARVAL1[i] + '\t')
        pvfile.writelines('\r\n')
        # Write parameter sets having one parameter deviate from the baseline parameter set
        for j in range(0,len(PARVAL1)):
            for i in range(0,len(PARVAL1)):
                if j == i:
                    if (float(PARVAL1[i]) * (1+PCT_DEV/100.) >= float(PARLBND[i])) & (float(PARVAL1[i]) * (1+PCT_DEV/100.) <= float(PARUBND[i])):
                        pvfile.writelines(str(float(PARVAL1[i]) * (1+PCT_DEV/100.)) + '\t')
                    elif (float(PARVAL1[i]) * (1+PCT_DEV/100.) > float(PARUBND[i])):
                        raise GeoAlgorithmExecutionException(PARNAME[i] + ' exceeds upper boundary with a deviation of '+ str(PCT_DEV)+' %.')
                    else:
                        raise GeoAlgorithmExecutionException(PARNAME[i] + ' is smaller than lower boundary with a deviation of '+ str(PCT_DEV)+' %.')
                else:
                    pvfile.writelines(PARVAL1[i] + '\t')
            pvfile.writelines('\r\n')
        pvfile.close()

    def getIcon(self):
        return  QtGui.QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

