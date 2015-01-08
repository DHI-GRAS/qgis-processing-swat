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
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.gui.Help2Html import getHtmlFromRstFile

from processing.core.ProcessingLog import ProcessingLog 

class SWATAlgorithm(GeoAlgorithm, object):

    def __init__(self, descriptionFile):
        super(SWATAlgorithm, self).__init__()
        self.descriptionFile = descriptionFile

    def help(self):
        [folder, filename] = os.path.split(self.descriptionFile)
        [filename, _] = os.path.splitext(filename)
        helpfile = os.path.join(folder, "doc", filename+".html")
        
        if os.path.exists(helpfile):
            return True, getHtmlFromRstFile(helpfile)
        else:
            return False, None
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

    
