"""
***************************************************************************
   ParVarFile.py
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

"""Class for interaction with model file"""
import os
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from numpy import size

class ParVarFile(GeoAlgorithmExecutionException):

    def __init__(self, parvar_file,NPAR):
        if os.path.isfile(parvar_file):
            # Model folder
            self.Path = os.path.split(parvar_file)[0]
            # Model file
            self.ParVarFile = parvar_file

            # Reading model file
            self.desc = {}
            # Getting variables from model file
            f=open(parvar_file,'r').readlines()
            if f[0].split() == NPAR:
                pass
            else:
                if size(f[1:]) < NPAR+1:
                    raise GeoAlgorithmExecutionException('Too few parameter sets in the parameter variation file: \"' + parvar_file + '\" ')
                elif size(f[1:]) > NPAR+1:
                    raise GeoAlgorithmExecutionException('Too many parameter sets in the parameter variation file: \"' + parvar_file + '\" ')
        else:
            raise GeoAlgorithmExecutionException('No such file: \"' + parvar_file + '\" ')
