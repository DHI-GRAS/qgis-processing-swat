"""
***************************************************************************
   OSFWF_GetGfsData.py
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
import GetGfsClimateData

class OSFWF_GetGfsData(SWATAlgorithm):

    PCP_DST_FOLDER = "PCP_DST_FOLDER"
    TMAX_DST_FOLDER = "TMAX_DST_FOLDER"
    TMIN_DST_FOLDER = "TMIN_DST_FOLDER"
    LEFT_LONG = "LEFT_LONG"
    RIGHT_LONG = "RIGHT_LONG"
    TOP_LAT = "TOP_LAT"
    BOTTOM_LAT = "BOTTOM_LAT"

    def __init__(self):
        SWATAlgorithm.__init__(self, __file__)

    def defineCharacteristics(self):
        self.name = "1.1 - Get new NOAA-GFS data (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_GetGfsData.PCP_DST_FOLDER, "Select precipitation folder", True))
        self.addParameter(ParameterFile(OSFWF_GetGfsData.TMAX_DST_FOLDER, "Select maximum temperature folder", True))
        self.addParameter(ParameterFile(OSFWF_GetGfsData.TMIN_DST_FOLDER, "Select minimum temperature folder", True))
        param = ParameterNumber(OSFWF_GetGfsData.LEFT_LONG, "Left longitude", -180, 180, -20)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetGfsData.RIGHT_LONG, "Right longitude", -180, 180, 55)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetGfsData.TOP_LAT, "Top latitude", -89, 89, 40)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetGfsData.BOTTOM_LAT, "Bottom latitude", -89, 89, -40)
        param.isAdvanced = True
        self.addParameter(param)

    def processAlgorithm(self, progress):
        # Do GFS processing here

        for var in ['APCP','TMAX','TMIN']:
            # Set destination folder and level
            if var == 'APCP':
                progress.setConsoleInfo("Downloading GFS precipitation data...")
                progress.setPercentage(0)
                dst_folder = self.getParameterValue(OSFWF_GetGfsData.PCP_DST_FOLDER)
                level = 'surface'
            elif var == 'TMAX':
                progress.setConsoleInfo("Downloading GFS maximum temperature data...")
                progress.setPercentage(0)
                dst_folder = self.getParameterValue(OSFWF_GetGfsData.TMAX_DST_FOLDER)
                level = '2_m_above_ground'
            elif var == 'TMIN':
                progress.setConsoleInfo("Downloading GFS minimum temperature data...")
                progress.setPercentage(0)
                dst_folder = self.getParameterValue(OSFWF_GetGfsData.TMIN_DST_FOLDER)
                level = '2_m_above_ground'

            # Setting coordinates
            left_long = math.floor(self.getParameterValue(OSFWF_GetGfsData.LEFT_LONG))
            right_long = math.ceil(self.getParameterValue(OSFWF_GetGfsData.RIGHT_LONG))
            top_lat = math.ceil(self.getParameterValue(OSFWF_GetGfsData.TOP_LAT))
            bottom_lat = math.ceil(self.getParameterValue(OSFWF_GetGfsData.BOTTOM_LAT))


            if (left_long >= right_long) or (bottom_lat >= top_lat):
                raise GeoAlgorithmExecutionException('Error in coordinates: \"Left :' + str(left_long) + \
                '< Right: ' + str(right_long) + ', Top :' + str(top_lat) + '> Bottom :' + str(bottom_lat) + '\"')

            if os.path.isdir(dst_folder):
                # Create and set Forecast folder
                forecast_folder = dst_folder + os.sep + 'Forecasts'
                if not os.path.isdir(forecast_folder):
                    os.mkdir(forecast_folder)

                # Creating log file
                log_file = open(dst_folder + os.sep + "Download_log.txt", "w")
                # Write current date to log file
                now = date.today()
                log_file.write(self.name + ' run: ' + now.strftime('%Y%m%d') + '\n')
                log_file.write('Data source: NOAA-GFS\n')

                # Finding newest file date and move old forecasted files to forecast folder
                dates = []
                dirs = os.listdir(dst_folder)
                for f in dirs:
                    if ( os.path.isfile(os.path.join(dst_folder,f)) ):
                        if (var + '.tif') in f:
                            dates.append(date(int(f[0:4]),int(f[4:6]),int(f[6:8])))
                        elif (var + '_Forecast_') in f:
                            shutil.copy(os.path.join(dst_folder,f),forecast_folder + os.sep + os.path.split(f)[1])
                            os.remove(os.path.join(dst_folder,f))

                # Newest file date +1 or today-60days (if no files) as start date
                if dates == []:
                    first_date = now - timedelta(days=60)
                else:
                    first_date = max(dates) + timedelta(days=1)
                log_file.write(var + ' downloading start date: ' + first_date.strftime('%Y%m%d') + '\n')

                # Downloading data
                forecast_date = GetGfsClimateData.GfsForecastImport(first_date, var, level, dst_folder, left_long, right_long, top_lat, bottom_lat, log_file, progress)
                log_file.write('Forecast date ' + var + ': ' + forecast_date.strftime('%Y%m%d') + '\n')

                log_file.close()

