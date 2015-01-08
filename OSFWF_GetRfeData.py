"""
***************************************************************************
   OSFWF_GetRfeData.py
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
import shutil
from datetime import date, timedelta, datetime
import math
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import *
from SWATAlgorithm import SWATAlgorithm
import GetRfeClimateData

class OSFWF_GetRfeData(SWATAlgorithm):

    TYPE = "TYPE"
    PCP_DST_FOLDER = "PCP_DST_FOLDER"
    START_DATE = "START_DATE"
    END_DATE = "END_DATE"
    SUBSET_EXTENT = "EXTENT"

    def __init__(self):
        super(OSFWF_GetRfeData, self).__init__(__file__)
    
    def defineCharacteristics(self):
        self.name = "1.2 - Get FEWS-RFE data (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_GetRfeData.PCP_DST_FOLDER, "Select precipitation folder", True, False))
        self.addParameter(ParameterString(OSFWF_GetRfeData.START_DATE, "Start date [yyyymmdd]. After 20010101.", "20130101", False))
        param = ParameterExtent(OSFWF_GetRfeData.SUBSET_EXTENT, "Subset to extent ", "0,1,0,1")
        param.isAdvanced = True
        self.addParameter(param)
        now = date.today()
        self.addParameter(ParameterString(OSFWF_GetRfeData.END_DATE, "End date [yyyymmdd]. From 2001 to " + str(now.year - 1) + " a minimum of one year will be downloaded.", now.strftime('%Y%m%d'), False))


    def processAlgorithm(self, progress):
        # Do RFE processing here
        dst_folder = self.getParameterValue(OSFWF_GetRfeData.PCP_DST_FOLDER)
        start_date = self.getParameterValue(OSFWF_GetRfeData.START_DATE)
        end_date = self.getParameterValue(OSFWF_GetRfeData.END_DATE)
        subset_extent = self.getParameterValue(OSFWF_GetRfeData.SUBSET_EXTENT)

        if os.path.isdir(dst_folder):
            # Creating log file
            log_file = open(dst_folder + os.sep + "Download_log.txt", "w")
            # Write current date to log file
            now = date.today()
            log_file.write(self.name + ' run: ' + now.strftime('%Y%m%d') + '\n')
            log_file.write('Data source: FEWS-RFE\n')

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
            iteration = 0
            for year in range(start_date.year,end_date.year+1):
                if year == now.year:
                    progress.setConsoleInfo("Downloading and extracting RFE precipitation data for " + str(year) + "...")
                    if start_date < date(now.year,1,1):
                        iteration = GetRfeClimateData.RfeImportDays(date(year,1,1),end_date,dst_folder,log_file,progress,iteration,number_of_iterations, subset_extent)
                    else:
                        iteration = GetRfeClimateData.RfeImportDays(start_date,end_date,dst_folder,log_file,progress,iteration,number_of_iterations, subset_extent)
                else:
                    progress.setConsoleInfo("Downloading RFE precipitation data for " + str(year) + "...")
                    iteration = GetRfeClimateData.RfeImportYear(year,dst_folder,log_file,progress,iteration,number_of_iterations, subset_extent)

            log_file.close()

        else:
            raise GeoAlgorithmExecutionException('No such directory: \"' + dst_folder + '\" ')

