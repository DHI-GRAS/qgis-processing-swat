"""
***************************************************************************
   ModelFile.py
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

class ModelFile(GeoAlgorithmExecutionException):

    def __init__(self, model_file):
        if os.path.isfile(model_file):
            # Model folder
            self.Path = os.path.split(model_file)[0]
            # Model file
            self.ModelFile = model_file

            # Reading model file
            self.desc = {}
            # Getting variables from model file
            f=open(model_file,'r').readlines()
            if not f[0].find('Model description file') == -1:
                for line in range(1,len(f)):
                    try:
                        (key, val) = f[line].split()
                        self.desc[key] = val
                    except:
                        pass
            else:
                raise GeoAlgorithmExecutionException('Not a model descibtion file: \"' + model_file + '\" ')
        else:
            raise GeoAlgorithmExecutionException('No such file: \"' + model_file + '\" ')
