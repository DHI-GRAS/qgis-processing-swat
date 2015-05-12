"""
***************************************************************************
   SWAT_PEST_specs.py
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

from SWAT_parameter_specs import SWAT_parameter_specs
from processing_SWAT.WG9HMUtils import WG9HMUtils
import os

parspecs = SWAT_parameter_specs()

class SWAT_PEST_specs():

    def __init__(self):
        # Modify this class to change settings for SWAT-PEST interaction

        # Folder where PEST executables are stored. 
        self.PESTexeFolder = os.path.join(WG9HMUtils.mapwindowPath(),'Plugins','MWSWAT2009','PEST') 

        # Parameter identifier used in PEST template files
        self.ptf = '$'

        # Observation identifies used in PEST instruction files
        self.pif = '$'

        # Location of simulated discharge in reach output file
        self.flowoutinicol = 50

        self.flowoutendcol = 61

        # PEST control file defaults

        self.CFfirstline = 'pcf'

        self.RSTFLE = 'restart'

        self.PESTMODE = 'estimation'

        self.NPARGP = len(parspecs.PARAMETERS)

        self.NPRIOR = 0

        self.NOBSGP = 1

        self.PRECIS = 'single'

        self.DPOINT = 'point'

        self.NUMCOM = 1

        self.JACFILE = 0

        self.MESSFILE = 0

        self.RLAMBDA1 = 10.0

        self.RLAMFAC = 2.0

        self.PHIRATSUF= 0.3

        self.PHIREDLAM = 0.01

        self.NUMLAM = 10

        self.RELPARMAX = 5.0

        self.FACPARMAX = 5.0

        self.FACORIG = 0.001

        self.PHIREDSWH = 0.1

        self.NOPTMAX = 30

        self.PHIREDSTP = 0.005

        self.NPHISTP = 4

        self.NPHINORED = 4

        self.RELPARSTP = 0.01

        self.NRELPAR = 4

        self.ICOV = 1

        self.ICOR = 1

        self.IEIG = 1
