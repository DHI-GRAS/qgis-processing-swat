"""
***************************************************************************
   GetRfeClimateData.py
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

import urllib
import tarfile
from datetime import date, timedelta
import os
import processing
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import osr
import shutil
import sys

def RfeImportYear(year, TargetDirectory, log_file, progress, iteration, number_of_iterations, subset_extent):
    """Importing and extracting FEWS RFE from web server for a given year."""
    # Set initial values
    iteration += 1
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary'
    BIL_filelist = []

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Downloading climate data
    try:
        UrlToRead ='http://earlywarning.usgs.gov/ftp2/bulkdailydata/africa/rfe2/years/rfe_' + str(year) + '.tar.gz'
        dst_file = DownloadDirectory + os.sep + 'rfe_' + str(year) + '.tar.gz'
        rday=urllib.urlretrieve(UrlToRead, dst_file)
        progress.setPercentage(iteration/number_of_iterations*100)
        iteration += 1
        progress.setConsoleInfo("Extracting data...")
        # Extract year
        tar = tarfile.open(dst_file)
        tar.extractall(DownloadDirectory)
        tar.close()
        # Extract days
        tar_dir = dst_file.split('.tar.gz')[0]
        if os.path.isdir(tar_dir):
            dirs = os.listdir(tar_dir)
            for f in dirs:
                dst_file = tar_dir + os.sep + f
                tar = tarfile.open(dst_file)
                tar.extractall(DownloadDirectory)
                tar.close()
                BIL_filelist.append(DownloadDirectory + os.sep + f.split('.tar.gz')[0] + '.bil')
        progress.setPercentage(iteration/number_of_iterations*100)
    except tarfile.ReadError:
        tar.close()
        os.remove(dst_file)

    # Translate to GeoTIFF
    iteration = Rfe2GeoTIFF_WGS84(BIL_filelist, TargetDirectory, log_file, progress, iteration, number_of_iterations, subset_extent)
    try:
        shutil.rmtree(DownloadDirectory) # Remove Temp dir
    except:
        pass
    return iteration

def RfeImportDays(startdate, enddate, TargetDirectory, log_file, progress, iteration, number_of_iterations, subset_extent):
    """Importing and extracting FEWS RFE from web server for a given year"""
    # Set initial values
    iteration += 2
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary'
    BIL_filelist = []

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Get date info
    FirstYear = startdate.year
    LastYear = enddate.year

    # Looping through years
    for i in range(FirstYear, LastYear+1):
        if i==FirstYear:
            StartDay = (startdate-date(FirstYear,1,1)).days+1
        else:
            StartDay = 1
        if i==LastYear:
            EndDay = (enddate-date(LastYear,1,1)).days+1
        else:
            EndDay = (date(i,12,31)-date(i,1,1)).days+1

        # Looping through days
        for j in range(StartDay, EndDay+1):
            # Downloading climate data
            try:
                daystr = str(i)+str(j)
                UrlToRead ='http://earlywarning.usgs.gov/ftp2/bulkdailydata/africa/rfe2/days/rain_' + daystr + '.tar.gz'
                dst_file = DownloadDirectory + os.sep + 'rain_' + daystr + '.tar.gz'
                rday=urllib.urlretrieve(UrlToRead, dst_file)
                # Extract
                tar = tarfile.open(dst_file)
                tar.extractall(DownloadDirectory)
                tar.close()
                BIL_filelist.append(dst_file.split('.tar.gz')[0] + '.bil')
            except tarfile.ReadError:
                try:
                    tar.close()
                except:
                    None
                os.remove(dst_file)

    progress.setPercentage(iteration/number_of_iterations*100)

    # Translate to GeoTIFF
    iteration = Rfe2GeoTIFF_WGS84(BIL_filelist, TargetDirectory, log_file, progress, iteration, number_of_iterations, subset_extent)
    try:
        shutil.rmtree(DownloadDirectory) # Remove Temp dir
    except:
        pass
    return iteration

def Rfe2GeoTIFF_WGS84(BIL_filelist, dst_folder, log_file, progress, iteration, number_of_iterations, subset_extent):
    """OBS: Files must be in WGS84 """

    iteration +=1
    progress.setConsoleInfo("Translating to GeoTIFF...")
    for BIL_filename in BIL_filelist:
        filename = os.path.split(BIL_filename)[1].split('.bil')[0]
        file_date = date(int(filename[5:9]),1,1) + timedelta(days=int(filename[9:])-1)
        TIFF_filename = dst_folder + os.sep + file_date.strftime('%Y%m%d') + '_' + filename[0:5] + '.tif'

        # check if the output file already exists and if it does try to delete it
##        try:
##            if os.path.exists(TIFF_filename):
##                os.remove(TIFF_filename)
##            call_gdal_translate(BIL_filename, TIFF_filename, subset_extent, progress)
##        except Exception, e:
##            progress.setText('Cannot remove existing file '+TIFF_filename+'. No update done on that file.')
        call_gdal_translate(BIL_filename, TIFF_filename, subset_extent, progress)
    progress.setPercentage(iteration/number_of_iterations*100)
    return iteration

def call_gdal_translate(in_filename, out_filename, newExtent, progress):

    try:
        inlayer = None

        try:
            # It would be easier to get the raster extents using QgsRasterLayer and not GDAL but
            # there is a bug in QgsRasterLayer that crashes QGIS "randomly" when opening a layer.
            # Maybe it's fixed in QGIS 2.0
            inlayer = gdal.Open(in_filename, GA_ReadOnly)
            #inlayer = dataobjects.getObjectFromUri(in_filename)
        except:
            progress.setConsoleInfo('Cannot get layer info ! Not subsetting.')
            return

        if not inlayer:
            progress.setConsoleInfo('Cannot get layer info !! Not subsetting.')
            return


        # get the raster extent coordinates using GDAL
        geoinformation = inlayer.GetGeoTransform(can_return_null = True)

        if geoinformation:
            cols = inlayer.RasterXSize
            rows = inlayer.RasterYSize
            tlX = geoinformation[0] # top left X
            tlY = geoinformation[3] # top left Y
            brX = geoinformation[0] + geoinformation[1] * cols + geoinformation[2] * rows # bottom right X
            brY = geoinformation[3] + geoinformation[4] * cols + geoinformation[5] * rows # bottom right Y

            xmin = min(tlX, brX)
            xmax = max(tlX, brX)
            ymin = min(tlY, brY)
            ymax = max(tlY, brY)
        else:
            progress.setText('Cannot get layer info !!! Not subsetting.')
            inlayer = None
            return
        inlayer = None

        # get the minimum extent of the subset extent and the file extent
        if not newExtent == "0,1,0,1":
            extents = newExtent.split(",")
            try:
                [nxmin, nxmax, nymin, nymax] = [float(i) for i in extents]
            except ValueError:
                progress.setText('Invalid subset extent ! Not subsetting.')
                return
            xmin = max(nxmin, xmin)
            xmax = min(nxmax, xmax)
            ymin = max(nymin, ymin)
            ymax = min(nymax, ymax)

        subsetExtent = str(xmin)+","+str(xmax)+","+str(ymin)+","+str(ymax)

        # call gdal_translateconvertformat
        progress.setText('Processing '+out_filename)
        print('Processing '+out_filename)
        #param = {'INPUT':in_filename, 'OUTSIZE':100, 'OUTSIZE_PERC':True, 'NO_DATA':"none", 'EXPAND':0, 'SRS':"EPSG:4326",'PROJWIN':subsetExtent,'SDS':False, 'EXTRA':'-co "COMPRESS=LZW"', 'OUTPUT':out_filename}
        #processing.runalg('gdalogr:translate',param)
        processing.runalg("gdalogr:translate",in_filename,100,True,"",0,"EPSG:4326",subsetExtent,False,5,4,75,6,1,False,0,False,"",out_filename)

    except Exception as e:
      #  progress.setText(sys.exc_info()[0])
         progress.setConsoleInfo('Fail')