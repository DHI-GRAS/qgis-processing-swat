"""
***************************************************************************
   SWAT_SENSAN_specs.py
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

parspecs = SWAT_parameter_specs()

class SWAT_SENSAN_specs():

    def __init__(self):
        # Modify this class to change settings for SWAT-PEST interaction

        # Folder where PEST executables are stored. Adjust depending on installation
        self.PESTexeFolder = 'c:\\Program Files(x86)\\MapWindow\\Plugins\\MWSWAT2009\\PEST' ##'c:\\Program Files (x86)\\PEST_13'

        # SENSAN control file defaults

        self.CFfirstline = 'scf'

        self.SCREENDISP = 'noverbose'

        self.NPARGP = len(parspecs.PARAMETERS)

        self.PRECIS = 'single'

        self.DPOINT = 'point'

        self.VARFLE = 'parvar.dat'

        self.ABSFLE = 'out1.dat'

        self.RELFLE = 'out2.dat'

        self.SENSFLE = 'out3.dat'

        self.RESULT_TYPES = ['RELFLE - relative differences between observation values']

