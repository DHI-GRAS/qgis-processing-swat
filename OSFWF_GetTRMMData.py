"""
***************************************************************************
   OSFWF_GetTRMMData.py
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

import shutil
import os
from datetime import date, timedelta, datetime
import math
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
import GetTRMMData
import datetime
from datetime import datetime

class OSFWF_GetTRMMData(SWATAlgorithm):

    PCP_DST_FOLDER = "PCP_DST_FOLDER"
    LEFT_LONG = "LEFT_LONG"
    RIGHT_LONG = "RIGHT_LONG"
    TOP_LAT = "TOP_LAT"
    BOTTOM_LAT = "BOTTOM_LAT"
    START_DATE = "START_DATE"
    END_DATE = "END_DATE"

    def __init__(self):
        SWATAlgorithm.__init__(self, __file__)

    def defineCharacteristics(self):
        self.name = "1.4 - Get TRMM3B42 v.7 data (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_GetTRMMData.PCP_DST_FOLDER, "Select precipitation folder", True))
        param = ParameterNumber(OSFWF_GetTRMMData.LEFT_LONG, "Left longitude", -180, 180, -20)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetTRMMData.RIGHT_LONG, "Right longitude", -180, 180, 55)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetTRMMData.TOP_LAT, "Top latitude", -50, 50, 40)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetTRMMData.BOTTOM_LAT, "Bottom latitude", -50, 50, -40)
        param.isAdvanced = True
        self.addParameter(param)
        self.addParameter(ParameterString(OSFWF_GetTRMMData.START_DATE, "Start date [yyyymmdd]. After 19980101.", "19980101", False))
        now = datetime.strptime('20151130', "%Y%m%d")
        self.addParameter(ParameterString(OSFWF_GetTRMMData.END_DATE, "End date [yyyymmdd]. From 19980102 to 20151130" + " - a minimum of one day will be downloaded.", now.strftime('%Y%m%d'), False))


    def processAlgorithm(self, progress):
        # Do RFE processing here
        TRMM = 'TRMM3B42'
        dst_folder = self.getParameterValue(OSFWF_GetTRMMData.PCP_DST_FOLDER)
        start_date = self.getParameterValue(OSFWF_GetTRMMData.START_DATE)
        end_date = self.getParameterValue(OSFWF_GetTRMMData.END_DATE)

		# Setting coordinates
        left_long = math.floor(self.getParameterValue(OSFWF_GetTRMMData.LEFT_LONG))
        right_long = math.ceil(self.getParameterValue(OSFWF_GetTRMMData.RIGHT_LONG))
        top_lat = math.ceil(self.getParameterValue(OSFWF_GetTRMMData.TOP_LAT))
        bottom_lat = math.ceil(self.getParameterValue(OSFWF_GetTRMMData.BOTTOM_LAT))
        dst_folder = self.getParameterValue(OSFWF_GetTRMMData.PCP_DST_FOLDER)

        if (left_long >= right_long) or (bottom_lat >= top_lat):
        	raise GeoAlgorithmExecutionException('Error in coordinates: \"Left :' + str(left_long) + \
        	'< Right: ' + str(right_long) + ', Top :' + str(top_lat) + '> Bottom :' + str(bottom_lat) + '\"')

        if os.path.isdir(dst_folder):
            # Creating log file
            log_file = open(dst_folder + os.sep + "Download_log.txt", "w")
            # Write current date to log file
            now = date.today()
            log_file.write(self.name + ' run: ' + now.strftime('%Y%m%d') + '\n')
            log_file.write('Data source: TRMM3B42 v.7\n')

            # Get dates
            try:
                start_date = datetime.strptime(start_date, "%Y%m%d").date()
            except:
                raise GeoAlgorithmExecutionException('Error in data format: \"' + start_date + '\". Must be in YYYYMMDD.')

            try:
                end_date = datetime.strptime(end_date, "%Y%m%d").date()
            except:
                raise GeoAlgorithmExecutionException('Error in data format: ' + end_date + '\". Must be in YYYYMMDD.')

            number_of_iterations = float((end_date.year-start_date.year +1)*3)

            # Download, extract and translate to GeoTIFF
            progress.setConsoleInfo("Downloading TRMM3B42 precipitation data...")
            progress.setPercentage(0)
            iteration = GetTRMMData.TRMM3B42v7Import(start_date, end_date, TRMM, dst_folder, left_long, right_long, top_lat, bottom_lat, log_file, progress)
            log_file.close()

        else:
            raise GeoAlgorithmExecutionException('No such directory: \"' + dst_folder + '\" ')

