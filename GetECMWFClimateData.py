"""
***************************************************************************
   GetECMWFClimateData.py
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

from ECMWFDataServer import ECMWFDataServer
from datetime import date, timedelta, datetime
import os
import urllib
import processing
from processing.tools import dataobjects
from processing.algs.grass.GrassUtils import GrassUtils
from osgeo import gdal
from gdalconst import *
import shutil
import osr

def ECMWFImport(email, token, startdate, enddate, tmax_dst_folder, tmin_dst_folder, LeftLon, RightLon, TopLat, BottomLat, progress):
    """Importing ECMWF temperature data using the
    ECMWFDataServer class provided by ECMWF"""
    DownloadDirectory = tmax_dst_folder + os.sep + 'Temporary'

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Get max enddate and min startdate from website
    UrlToRead = 'http://data-portal.ecmwf.int/data/d/interim_full_daily/'
    dst_file = DownloadDirectory + os.sep + 'Portal_site.txt'
    urllib.urlretrieve(UrlToRead, dst_file)
    text = open(dst_file,'r').read()
    index = text.find('<span id="date_end_date">')
    max_enddate = datetime.strptime((text[index+25:index+35]), "%Y-%m-%d").date()
    index = text.find('<span id="date_start_date">')
    min_startdate = datetime.strptime((text[index+27:index+37]), "%Y-%m-%d").date()
    if startdate < min_startdate:
        startdate = min_startdate
        progress.setConsoleInfo("Start date corrected to: " + startdate.strftime('%Y%m%d') + "...")
    if enddate > max_enddate:
        enddate = max_enddate
        progress.setConsoleInfo("End date corrected to: " + enddate.strftime('%Y%m%d') + "...")
    if startdate > max_enddate:
        return

    # Get dates
    FirstYear = startdate.year
    FirstMonth = startdate.month
    FirstDay = startdate.day
    LastYear = enddate.year
    LastMonth = enddate.month
    LastDay = enddate.day
    now = date.today()

    # Start data server
    server = ECMWFDataServer(
           'http://data-portal.ecmwf.int/data/d/dataserver/',
           token,email)

    # Run one year at a time
    for year in range(FirstYear,LastYear+1):
        dst_file = DownloadDirectory + os.sep + str(year) + '.grb'
        if year == LastYear:
            if FirstYear < LastYear:
                first_month = 1
            else:
                first_month = FirstMonth

            for m in range(first_month,LastMonth+1):
                progress.setConsoleInfo("Downloading ECMWF temperature data for " + str(year) + " month " + str(m) + "...")
                if m == LastMonth:
                    GetECMWF(server, year, m, 1, year, m, LastDay, LeftLon, RightLon, TopLat, BottomLat, dst_file)
                else:
                    end_month = date(year,1+m,1) - timedelta(days=1)
                    GetECMWF(server, year, m, 1, year, m, end_month.day, LeftLon, RightLon, TopLat, BottomLat, dst_file)
                # Translate to GeoTIFF
                tiff_filelist = gdal2GeoTiff_ECMWF_WGS84(dst_file, progress)

                # Do map calculations
                Max_Daily_FileList, Min_Daily_FileList = ECMWF2DailyMaps(tiff_filelist, progress)

                # Move files and clean up
                for f in Max_Daily_FileList:
                    shutil.copy(f, tmax_dst_folder + os.sep + os.path.split(f)[1])
                    os.remove(f)
                for f in Min_Daily_FileList:
                    shutil.copy(f, tmin_dst_folder + os.sep + os.path.split(f)[1])
                    os.remove(f)

        else:
            for m in range(1,12+1):
                progress.setConsoleInfo("Downloading ECMWF temperature data for " + str(year) + " month " + str(m) + "...")
                if m == 12:
                    GetECMWF(server, year, m, 1, year, m, 31, LeftLon, RightLon, TopLat, BottomLat, dst_file)
                else:
                    end_month = date(year,1+m,1) - timedelta(days=1)
                    GetECMWF(server, year, m, 1, year, m, end_month.day, LeftLon, RightLon, TopLat, BottomLat, dst_file)

                # Translate to GeoTIFF
                tiff_filelist = gdal2GeoTiff_ECMWF_WGS84(dst_file, progress)

                # Do map calculations
                Max_Daily_FileList, Min_Daily_FileList = ECMWF2DailyMaps(tiff_filelist, progress)

                # Move files and clean up
                for f in Max_Daily_FileList:
                    shutil.copy(f, tmax_dst_folder + os.sep + os.path.split(f)[1])
                    os.remove(f)
                for f in Min_Daily_FileList:
                    shutil.copy(f, tmin_dst_folder + os.sep + os.path.split(f)[1])
                    os.remove(f)

        shutil.rmtree(DownloadDirectory) # Remove Temp dir


    server = None


def GetECMWF(server, FirstYear, FirstMonth, FirstDay, LastYear, LastMonth, LastDay, LeftLon, RightLon, TopLat, BottomLat, dst_file):
    server.retrieve({
        'dataset' : "interim_full_daily",
        'date'    : str(FirstYear) + str(FirstMonth).zfill(2) + str(FirstDay).zfill(2) + '/to/' + str(LastYear) + str(LastMonth).zfill(2) + str(LastDay).zfill(2),
        'time'    : "00:00:00/06:00:00/12:00:00/18:00:00",
        'grid'    : "1/1",
        'step'    : "0",
        'levtype' : "sfc",
        'type'    : "an",
        'param'   : "167.128",
        'area'    : str(TopLat) + '/' + str(LeftLon) + '/' + str(BottomLat) + '/' + str(RightLon),
        'target'  : dst_file
        })

    return

def gdal2GeoTiff_ECMWF_WGS84(Filename, progress):
    progress.setConsoleInfo("Translating to GeoTIFF...")
    tiff_filename_base = os.path.split(Filename)[0] + os.sep
    tiff_filelist = []

    d=datetime(1970,1,1)

    # Read raster bands from file
    data = gdal.Open(Filename, GA_ReadOnly)
    number_of_bands = data.RasterCount

    # Get extent
    layer = dataobjects.getObjectFromUri(Filename)
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())

    for i in range(1,number_of_bands+1):
        data = gdal.Open(Filename, GA_ReadOnly)
        band = data.GetRasterBand(i)
        htime = band.GetMetadata()['GRIB_REF_TIME']
        userange = len(htime)-7
        UTCtime_delta = int(band.GetMetadata()['GRIB_REF_TIME'][0:userange])
        data = None
        tiff_filename = tiff_filename_base + str((d + timedelta(seconds=UTCtime_delta)).year) + \
                        str((d + timedelta(seconds=UTCtime_delta)).month).zfill(2) + \
                        str((d + timedelta(seconds=UTCtime_delta)).day).zfill(2) + '_' + \
                        str((d + timedelta(seconds=UTCtime_delta)).hour).zfill(2) + 'ECMWF.tif'

        # Convert to GeoTIFF using processing GDAL
        param = {'INPUT':Filename, 'OUTSIZE':100, 'OUTSIZE_PERC':True, 'NO_DATA':"none", 'EXPAND':0, 'SRS':'', 'PROJWIN':extent, 'SDS':False, 'EXTRA':'-b '+str(i), 'OUTPUT':tiff_filename}
        processing.runalg("gdalogr:translate",param)
        tiff_filelist.append(tiff_filename)

        # Set projection to WGS84
        data = gdal.Open(tiff_filename, GA_Update)
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS( 'WGS84' )
        data.SetProjection( srs.ExportToWkt() )
        srs = None
        # Closing dataset
        data = None

    data = None
    return tiff_filelist

def ECMWF2DailyMaps(filelist, progress):
    progress.setConsoleInfo("Computing daily maps...")
    # Get all days
    dates = []
    Tmax_Daily_FileList = []
    Tmin_Daily_FileList = []
    for f in filelist:
        dates.append(os.path.split(f)[1][0:8])

    # Get unique dates
    unique_dates = list(set(dates))

    layer = dataobjects.getObjectFromUri(filelist[0])
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())


    # Calculate daily maps
    for datestr in unique_dates:
        # If all four daily maps exist
        if dates.count(datestr) == 4:
            maps = []
            # Get the four maps
            for f in filelist:
                if (datestr in f):
                    maps.append(f)

            # Do map calculations using processing GRASS
            # TMAX
            out_file = os.path.split(maps[0])[0] + os.sep + datestr + '_TMAX_' + 'ECMWF' + '.tif'
            Tmax_Daily_FileList.append(out_file)
            formula = 'max(A,B,C,D)'
            param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3], 'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file}
            processing.runalg("grass:r.mapcalculator", param)

            # TMIN
            out_file = os.path.split(maps[0])[0] + os.sep + datestr + '_TMIN_' + 'ECMWF' + '.tif'
            Tmin_Daily_FileList.append(out_file)
            formula = 'min(A,B,C,D)'
            param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3], 'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file}
            processing.runalg("grass:r.mapcalculator", param)


    return Tmax_Daily_FileList, Tmin_Daily_FileList

def DoMapCalc(maps, out_file, formula):
    layer = dataobjects.getObjectFromUri(maps[0])
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
    param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3], 'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file}
    processing.runalg("grass:r.mapcalculator", param)