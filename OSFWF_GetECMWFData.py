"""
***************************************************************************
   OSFWF_GetECMWFData.py
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
from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.parameters.ParameterFile import ParameterFile
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterString import ParameterString

import GetECMWFClimateData

class OSFWF_GetECMWFData(GeoAlgorithm):

    TMAX_DST_FOLDER = "TMAX_DST_FOLDER"
    TMIN_DST_FOLDER = "TMIN_DST_FOLDER"
    START_DATE = "START_DATE"
    END_DATE = "END_DATE"
    EMAIL = "EMAIL"
    TOKEN = "TOKEN"
    LEFT_LONG = "LEFT_LONG"
    RIGHT_LONG = "RIGHT_LONG"
    TOP_LAT = "TOP_LAT"
    BOTTOM_LAT = "BOTTOM_LAT"

    def defineCharacteristics(self):
        self.name = "1.3 - Get ECMWF data (OSFWF)"
        self.group = "Operational simulation and forecasting workflow (OSFWF)"
        self.addParameter(ParameterFile(OSFWF_GetECMWFData.TMAX_DST_FOLDER, "Select maximum temperature folder", True, False))
        self.addParameter(ParameterFile(OSFWF_GetECMWFData.TMIN_DST_FOLDER, "Select minimum temperature folder", True, False))
        self.addParameter(ParameterString(OSFWF_GetECMWFData.START_DATE, "Start date [yyyymmdd]. After 19790101.", "20120101", False))
        self.addParameter(ParameterString(OSFWF_GetECMWFData.END_DATE, "End date [yyyymmdd]. It is recomended that no more than 6 months of data is downloaded at a time.", "20120601", False))
        self.addParameter(ParameterString(OSFWF_GetECMWFData.EMAIL, "Email", "pbau@env.dtu.dk", False))
        self.addParameter(ParameterString(OSFWF_GetECMWFData.TOKEN, "Token", "c1f19168ccbfe27be455dd20acaa9a42", False))
        param = ParameterNumber(OSFWF_GetECMWFData.LEFT_LONG, "Left longitude", -180, 180, -20)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetECMWFData.RIGHT_LONG, "Right longitude", -180, 180, 55)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetECMWFData.TOP_LAT, "Top latitude", -89, 89, 40)
        param.isAdvanced = True
        self.addParameter(param)
        param = ParameterNumber(OSFWF_GetECMWFData.BOTTOM_LAT, "Bottom latitude", -89, 89, -40)
        param.isAdvanced = True
        self.addParameter(param)

    def processAlgorithm(self, progress):
        # Get inputs
        tmax_dst_folder = self.getParameterValue(OSFWF_GetECMWFData.TMAX_DST_FOLDER)
        tmin_dst_folder = self.getParameterValue(OSFWF_GetECMWFData.TMIN_DST_FOLDER)
        start_date = self.getParameterValue(OSFWF_GetECMWFData.START_DATE)
        end_date = self.getParameterValue(OSFWF_GetECMWFData.END_DATE)
        email = self.getParameterValue(OSFWF_GetECMWFData.EMAIL)
        token = self.getParameterValue(OSFWF_GetECMWFData.TOKEN)

        # Setting coordinates
        left_long = math.floor(self.getParameterValue(OSFWF_GetECMWFData.LEFT_LONG))
        right_long = math.ceil(self.getParameterValue(OSFWF_GetECMWFData.RIGHT_LONG))
        top_lat = math.ceil(self.getParameterValue(OSFWF_GetECMWFData.TOP_LAT))
        bottom_lat = math.ceil(self.getParameterValue(OSFWF_GetECMWFData.BOTTOM_LAT))

        # Check coordinates
        if (left_long >= right_long) or (bottom_lat >= top_lat):
            raise GeoAlgorithmExecutionException('Error in coordinates: \"Left :' + str(left_long) + \
            '< Right: ' + str(right_long) + ', Top :' + str(top_lat) + '> Bottom :' + str(bottom_lat) + '\"')

        # Get dates
        try:
            start_date = datetime.strptime(start_date, "%Y%m%d").date()
        except:
            raise GeoAlgorithmExecutionException('Error in data format: \"' + start_date + '\". Must be in YYYYMMDD.')

        try:
            end_date = datetime.strptime(end_date, "%Y%m%d").date()
        except:
            raise GeoAlgorithmExecutionException('Error in data format: ' + end_date + '\". Must be in YYYYMMDD.')

        if os.path.isdir(tmax_dst_folder) and os.path.isdir(tmin_dst_folder):

            # Download, extract and translate to GeoTIFF
            GetECMWFClimateData.ECMWFImport(email, token, start_date, end_date, tmax_dst_folder, tmin_dst_folder, left_long, right_long, top_lat, bottom_lat, progress)

        else:
            raise GeoAlgorithmExecutionException('No such directory: \"' + dst_folder + '\" ')

    def getIcon(self):
        return  QtGui.QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")

    def helpFile(self):
        [folder, filename] = os.path.split(__file__)
        [filename, _] = os.path.splitext(filename)
        helpfile = str(folder) + os.sep + "doc" + os.sep + filename + ".html"
        if os.path.exists(helpfile):
            return helpfile
        else:
            raise WrongHelpFileException("Sorry, no help is available for this algorithm.")
