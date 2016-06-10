"""
***************************************************************************
   GetGfsClimateData.py
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
from datetime import date, timedelta, datetime
import os
import processing
from processing.tools import dataobjects
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import osr
import shutil

def GfsForecastImport(StartDate, GfsVar, level, TargetDirectory, LeftLon, RightLon, TopLat, BottomLat, log_file, progress):
    """Importing available NOAA-GFS precipitation and temperature data for the 00 Cycle."""
    # Set initial values
    number_of_days = (date.today() - StartDate).days + 1
    number_of_files = (number_of_days-1)*4 + 32
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary'
    first = True
    FileList = []

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    iteration = 0
    # Downloading climate data
    for n in range(number_of_days,0,-1):
        day = StartDate + timedelta(days=n-1)
        IssueYear = day.year
        IssueMonth = day.month
        IssueDay = day.day
        IssueHour = 0
        daystr = str(IssueYear)+str(IssueMonth).zfill(2)+str(IssueDay).zfill(2)+str(IssueHour).zfill(2)
        # Forecast is 6 - 192 hours, else 6 - 24
        for i in range(6,192+1,6):
            if (i <= 24) or (first):
                iteration +=1
                progress_percent = iteration / float(number_of_files) * 100

                # This is the download string for 25-km resolution data (from 14th Jan 2015)
                # http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t12z.pgrb2.0p50.f006&lev_surface=on&var_APCP=on&subregion=&leftlon=-20&rightlon=55&toplat=40&bottomlat=-40&dir=%2Fgfs.2015011812
                if day >= date(2015,1,14):
                    UrlToRead =('http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p50.pl?file=gfs.t' + str(IssueHour).zfill(2) +
                        'z.pgrb2full.0p50.f' + str(i).zfill(3)+ '&lev_' + level + '=on&var_' +
                        GfsVar + '=on&subregion=&leftlon=' + str(LeftLon) + '&rightlon=' + str(RightLon) +
                        '&toplat=' + str(TopLat) + '&bottomlat=' + str(BottomLat) + '&dir=%2Fgfs.' +
                        daystr)
				# This is the download string for 50-km resolution data (before 14th Jan 2015)
                else:
                    UrlToRead =('http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_hd.pl?file=gfs.t' + str(IssueHour).zfill(2) +
                        'z.mastergrb2f' + str(i).zfill(2)+ '&lev_' + level + '=on&var_' +
                        GfsVar + '=on&subregion=&leftlon=' + str(LeftLon) + '&rightlon=' + str(RightLon) +
                        '&toplat=' + str(TopLat) + '&bottomlat=' + str(BottomLat) + '&dir=%2Fgfs.' +
                        daystr + '%2Fmaster')

                dst_file = DownloadDirectory + os.sep + str(IssueYear)+str(IssueMonth).zfill(2)+str(IssueDay).zfill(2) + '_' + str(i).zfill(2) + '_'  + 'GFS_' + GfsVar + '.grb'
                urllib.urlretrieve(UrlToRead, dst_file)
                # Show progress
                progress.setPercentage(progress_percent)
                if (i == 192):
                    ForecastDate = day
                    first = False
                text = open(dst_file,'r').read()
                # Check if data is issued on the given day
                if text.find('data file is not present') == -1 and text.find('Not Found') == -1:
                    FileList.append(dst_file)
                else:
                    os.remove(dst_file)
                    break

    # Convert GRIB files to GeoTIFF
    progress.setConsoleInfo("Translating to GeoTIFF...")
    progress.setPercentage(0)
    TIFF_FileList = gdal2GeoTiff_GFS_WGS84(FileList, log_file, progress)

    # Convert to daily maps
    progress.setConsoleInfo("Computing daily maps...")
    progress.setPercentage(0)
    Daily_FileList = Gfs2DailyMaps(TIFF_FileList, ForecastDate, GfsVar, log_file, progress)

    # Move files and clean up
    for f in Daily_FileList:
        shutil.copy(f, TargetDirectory + os.sep + os.path.split(f)[1])
    try:
        for f in Daily_FileList:
            os.remove(f)
        shutil.rmtree(DownloadDirectory) # Remove Temp dir
    except:
        pass

    return ForecastDate


def gdal2GeoTiff_GFS_WGS84(FileList, log_file, progress):
    """Translates from GDAL compatible data source to GeoTIFF files.

    OBS: Files must be WGS84"""
    tiff_FileList = []
    iteration = 0

    for f in FileList:
        iteration += 1
        # Append new filename to list
        tiff_filename = os.path.split(f)[0] + os.sep + os.path.split(f)[1].split('.grb')[0] + '.tif'
        tiff_FileList.append(tiff_filename)

        # Convert to GeoTIFF using processing GDAL
        layer = dataobjects.getObjectFromUri(f)
        extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
        #param = {'INPUT':f, 'OUTSIZE':100, 'OUTSIZE_PERC':True, 'NO_DATA':"none", 'EXPAND':0, 'SRS':'', 'PROJWIN':extent, 'SDS':False, 'EXTRA':'', 'OUTPUT':tiff_filename}
        #processing.runalg("gdalogr:translate",param)
        processing.runalg("gdalogr:translate",f,100,True,"",0,"",extent,False,5,4,75,6,1,False,0,False,"",tiff_filename)

        # Update geo-reference as GFS files longtitude of 55 degree is referenced as 360 + 55 = 415 degree
        data = gdal.Open(tiff_filename, GA_Update)
        geotransform = data.GetGeoTransform()
        # geotransform[0]: top left x
        # geotransform[1]: w-e pixel resolution
        # geotransform[2]: rotation, 0 if image is "north up"
        # geotransform[3]: top left y
        # geotransform[4]: rotation, 0 if image is "north up"
        # geotransform[5]: n-s pixel resolution
        if (geotransform[0] + geotransform[1] * data.RasterXSize) > 360:
            # Set left longitude
            geotransform = [geotransform[0]-360, geotransform[1], geotransform[2], geotransform[3], geotransform[4], geotransform[5]]
            data.SetGeoTransform(geotransform)

        # Set projection to WGS84
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS( 'WGS84' )
        data.SetProjection( srs.ExportToWkt() )
        srs = None

        # Closing dataset
        data = None

        # Show progress
        progress.setPercentage(iteration/float(len(FileList)) * 100)

    return tiff_FileList

def Gfs2DailyMaps(FileList, ForecastDate, GfsVar, log_file, progress):
    iteration = 0
    # Set map calculation formula
    if GfsVar == 'APCP':
        # Daily sum
        formula = 'A+B+C+D'
    elif GfsVar == 'TMAX':
        # Daily max
        formula = 'max(A,B,C,D)'
    elif GfsVar == 'TMIN':
        # Daily min
        formula = 'min(A,B,C,D)'

    # Get all days
    dates = []
    Daily_FileList = []
    Forecast_FileList = []
    for f in FileList:
        if ForecastDate.strftime('%Y%m%d') in f:
            Forecast_FileList.append(f)
        else:
            dates.append(os.path.split(f)[1][0:8])

    # ======= non forecasted days ================
    # Get unique dates
    unique_dates = list(set(dates))

    # Calculate daily maps
    for datestr in unique_dates:
        iteration += 4
        # If all four daily maps exist
        if dates.count(datestr) == 4:
            maps = []
            # Get the four maps
            for f in FileList:
                if (datestr in f):
                    maps.append(f)

            # Do map calculations using processing GRASS
            out_file = os.path.split(maps[0])[0] + os.sep + datestr + '_' + GfsVar + '.tif'
            Daily_FileList.append(out_file)
            DoMapCalc(maps, out_file, formula)

        # Show progress
        progress.setPercentage(iteration / float(len(FileList))*100)

    # ======= forecasted days ================
    # Calculate daily forecast maps
    if len(Forecast_FileList) == 32:
        for i in range( 0, (len(Forecast_FileList) / 4)):
            maps = ['']*4
            iteration += 4
            for f in Forecast_FileList:
                if ForecastDate.strftime('%Y%m%d') + '_' + str(i*24+6).zfill(2) + '_' in f:
                    maps[0] = f
                elif ForecastDate.strftime('%Y%m%d') + '_' + str(i*24+12) + '_' in f:
                    maps[1] = f
                elif ForecastDate.strftime('%Y%m%d') + '_' + str(i*24+18) + '_' in f:
                    maps[2] = f
                elif ForecastDate.strftime('%Y%m%d') + '_' + str(i*24+24) + '_' in f:
                    maps[3] = f

            # Do map calculations using processing GRASS
            forecasted_date = (ForecastDate + timedelta(days=i)).strftime('%Y%m%d')
            out_file = os.path.split(maps[0])[0] + os.sep + forecasted_date + '_' + GfsVar + '_Forecast_' + ForecastDate.strftime('%Y%m%d') + '.tif'
            Daily_FileList.append(out_file)
            DoMapCalc(maps, out_file, formula)

            # Show progress
            progress.setPercentage(iteration / float(len(FileList))*100)

    return Daily_FileList

def DoMapCalc(maps, out_file, formula):
    layer = dataobjects.getObjectFromUri(maps[0])
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
    param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3], 'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file}
    processing.runalg("grass:r.mapcalculator", param)