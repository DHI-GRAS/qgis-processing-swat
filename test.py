#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      s113332
#
# Created:     19/02/2016
# Copyright:   (c) s113332 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib2
from datetime import datetime, timedelta, date
import urllib
import os
import processing
from processing.tools import dataobjects
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import osr
import shutil
import sys
import os
import os.path
import numpy as np
from numpy import ma
import scipy.io

TargetDirectory = 'C:\\Users\\s113332\\Documents\\TRMM\\Test\\'
DownloadDirectory = TargetDirectory + 'Download' + os.sep


#Set initial values
startDate=datetime(1998,1,1)
endDate=datetime(1998,1,3)
number_of_days = (endDate - startDate).days
number_of_files = number_of_days*8
extent = str(-22.0) +',' +str(55.0)+ ',' + str(-40.0) + ',' + str(40.0) ##Set extent to crop from global map (min longitude, max longitude, min latitude, max latitude)
#extent = '-22.0, 55.0, -40.0, 40.0'
iteration = 0

#Set TRMM variables for download
TRMMVar = 'TRMM3B42'
product=TRMMVar[4:8]
urlBase='ftp://disc2.nascom.nasa.gov/data/TRMM/Gridded/3B42_V7'
tail='z.7.precipitation.bin'
var='nlat[0:1:399],nlon[0:1:1439],precipitation[0:1:1439][0:1:399]'

#Define and create necessary paths
DownloadDirectory = TargetDirectory + os.sep + 'Download' + os.sep   # Download directory contains downloaded .bin files.
GlobalDirectory = DownloadDirectory + os.sep + 'Tiff_files' + os.sep # Global will save global tiff files - direct conversion from bin files, if asked for
TemporaryDirectory = TargetDirectory + os.sep + 'Temporary' + os.sep # Temporary directory contains temporary cropped files before merging to daily values
if not os.path.isdir(TargetDirectory):
    os.mkdir(TargetDirectory)
if not os.path.isdir(TemporaryDirectory):
    os.mkdir(TemporaryDirectory)

# Create Temp download folder
if not os.path.isdir(DownloadDirectory):
    os.mkdir(DownloadDirectory)
    os.mkdir(GlobalDirectory)

#loop through the start,end months
FileList = []
iteration = 0
iDate=startDate

while iDate<=endDate:

    iteration +=1
    progress_percent = iteration / float(number_of_files) * 100

    iYear="%04d"%(iDate.year)
    iMonth="%02d"%(iDate.month)
    iDay="%02d"%(iDate.day)
    iDOY="%03d"%iDate.timetuple().tm_yday
    iYMD=iYear[2:4]+iMonth+iDay

    progress_percent = iteration / float(number_of_files) * 100

    # output file saved to DownloadDirectory, with name convention "3B43_yymmdd.hhz.7.precipitation.bin*
    for n in range(0,24,3):
        UrlToRead = urlBase + '/' + iYear + iMonth + '/' + product +'.'+iYMD +'.'+str(n).zfill(2)+ tail
        dst_file = DownloadDirectory + product + '.' + iYMD + '.'+str(n).zfill(2)+tail
        if os.path.isfile(dst_file) == False:
            outfp = open(dst_file,'wb')
            outfp.write(urllib2.urlopen(UrlToRead).read())
            iteration += 1
            progress.setPercentage(progress_percent)
            outfp.close()

        text = open(dst_file,'r').read()
        # Check if data is issued on the given day
        if text.find('data file is not present') == -1 and text.find('Not Found') == -1:
            FileList.append(dst_file)
        else:
            os.remove(dst_file)
            break

    iDate+=timedelta(days=1)


    tiff_FileList = []
for f in FileList:
    # Append new filename to list

    if f.endswith(tail):
        tiff_filename = TemporaryDirectory + 'globalmap.tif' #Save in temporary folder
        out_filename = os.path.split(f)[0] + os.sep + os.path.split(f)[1].split(tail)[0]+'cropped.tif'
        tiff_FileList.append(out_filename)

    ## From TRMM3B42 (Farago, 2015)
        """Step 1 """
        fp1 = open(f, 'rb')
        data_string1 = fp1.read()
        fp1.close()

    """ Step 2."""
    ## the data are recorded like "4-byte float"
    dt=np.dtype('>f4')
    array = np.fromstring(data_string1, dt)
    array=array.reshape((400, 1440))
    array=np.asarray(array, dtype='Float32')
    array = np.flipud(array)
    """ Step 3 """
    output_raster1 = gdal.GetDriverByName('GTiff').Create(tiff_filename,1440, 400, 1, gdal.GDT_Float32)
    geotransform = (-180, 0.25 ,0.0 ,50, 0.0, -0.25)
        # geotransform[0]: top left x
        # geotransform[1]: w-e pixel resolution
        # geotransform[2]: rotation, 0 if image is "north up"
        # geotransform[3]: top left y
        # geotransform[4]: rotation, 0 if image is "north up"
        # geotransform[5]: n-s pixel resolution
    output_raster1.SetGeoTransform(geotransform)
    outband = output_raster1.GetRasterBand(1)
    outband.WriteArray(array)
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')                ## Set the projection: WGS84
    output_raster1.SetProjection( srs.ExportToWkt() )
    output_raster1.GetRasterBand(1).WriteArray(array)

    #Reinitialize
    outband = None
    iceraster = None
    output_raster1 = None
    outarray = None
    array = None
    srs = None

    #Crop to Africa
    """ Step 4"""
    processing.runalg("gdalogr:translate",tiff_filename,100,True,"-9999.9",0,"",extent,False,5,4,75,6,1,False,0,False,"",out_filename)
dates = []
Daily_FileList = []
for f in tiff_FileList:
	dates.append(os.path.split(f)[1][5:11])
##
### Get unique dates
unique_dates = list(set(dates))
##
### Calculate daily maps
for datestr in unique_dates:
	# If all eight daily maps exist
    if dates.count(datestr) == 8:
        maps = []
    	# Get the eight maps
        for f in tiff_FileList:
            if (datestr in f):
                maps.append(f)
