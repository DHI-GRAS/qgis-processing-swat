"""
***************************************************************************
   SWAT_output_format_specs.py
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

class SWAT_output_format_specs():

    def __init__(self):
        # Modify this class if format of SWAT output files changes
        self.RESULT_TYPES = ['REACH', 'SUB-BASIN', 'HRU', 'RESERVOIR', 'HRU IMPOUNDMENT', 'STANDARD', 'INPUT SUMMARY']

        self.RESULT_VARIABLES = ['AREA', 'FLOW_IN', 'FLOW_OUT', 'EVAP', 'TLOSS', 'SURQ', 'SW', 'PRECIP', 'IRR', 'PET', 'ET', 'SW_INIT', 'SW_END', 'PERC', 'GW_RCHG', 'DA_RCHG', 'REVAP', 'SA_IRR', 'DA_IRR','SA_ST', 'DA_ST', 'SURQ_GEN', 'SURQ_CNT', 'LATQ', 'GW_Q', 'WYLD', 'DAILYCN', 'LAI', 'WTAB', 'WTABELO', 'VOLUME', 'SEEPAGE','TMP_MXdgC','TMP_MNdgC', 'CMETAL#1', 'CMETAL#2', 'CMETAL#3']

        self.REACH_RES_COLS = [4,5,6,7,8,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,44,45,46]

        self.SUB_RES_COLS = [4,-1,-1,-1,-1,11,9,5,-1,7,8,-1,-1,10,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,12,13,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]

        self.HRU_RES_COLS = [6,-1,-1,-1,25,-1,-1,7,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,26,27,28,29,71,75,76,-1,-1,31,32,-1,-1,-1]

        self.RSV_RES_COLS = [-1,4,5,7,-1,-1,-1,6,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,3,8,-1,-1,-1,-1,-1]

        self.REACH_UNITS = ['km^2', 'm^3/s', 'm^3/s', 'm^3/s', 'm^3/s', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'kg/day', 'kg/day', 'kg/day']

        self.SUB_UNITS = ['km^2', '', '', '', '','mm', 'mm', 'mm', '', 'mm', 'mm', '', '', 'mm', '', '', '', '', '', '', '', '', '', '', 'mm', 'mm', '', '', '', '', '', '', '', '', '', '', '']

        self.HRU_UNITS = ['km^2', '', '', '', 'mm', '', '', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', 'mm', '-', '-', 'mm', 'mm', '', '','C', 'C', '', '', '']

        self.RSV_UNITS = ['', 'm^3/s', 'm^3/s', 'm^3', '', '', '', 'm^3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'm^3', 'm^3', '', '', '', '', '']

##        self.REACH_DELIMITER = [5,5,9,6,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,
##            12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12]
##
##        self.SUB_DELIMITER = [6,4,9,5,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
##
##        self.HRU_DELIMITER = [4,5,6,7,5,5,5,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,
##            10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,
##            10,10,10,10,10,10,10,10,10,10,10,10,10,10]

        self.REACH_SKIPROWS = 9

        self.SUB_SKIPROWS = 9

        self.HRU_SKIPROWS = 9

        self.RSV_SKIPROWS = 9

        self.REACH_OUTNAME = 'output.rch'

        self.SUB_OUTNAME = 'output.sub'

        self.HRU_OUTNAME = 'output.hru'

        self.RSV_OUTNAME = 'output.rsv'

        #...............................................................................
        # Offset between Python date and EXCEL date in days. Can be adjusted

        self.PYEX_DATE_OFFSET = 693594

        #...............................................................................
