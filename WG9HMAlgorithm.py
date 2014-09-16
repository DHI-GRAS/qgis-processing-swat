"""
***************************************************************************
   WG9HMAlgorithm.py
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
from PyQt4.QtGui import *
from processing.script.ScriptAlgorithm import ScriptAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException

class WG9HMAlgorithm(ScriptAlgorithm):

    def helpFile(self):
        [folder, filename] = os.path.split(self.descriptionFile)
        [filename, _] = os.path.splitext(filename)
        folder = os.path.dirname(folder)
        helpfile = str(folder) + os.sep + "doc" + os.sep + filename + ".html"
        if os.path.exists(helpfile):
            return helpfile
        else:
            raise WrongHelpFileException("Sorry, no help is available for this algorithm.")
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")
    
    def getCopy(self):
        newone = WG9HMAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
    
